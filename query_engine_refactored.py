"""
Refactored GPTTutor Query Engine with modular architecture
"""
import json
import faiss
import numpy as np
import sys
import traceback
import re
import spacy
import time
from typing import Dict, List, Any, Optional

from config import Config
from api_response import APIResponse, AnswerData
from answer_processor import AnswerProcessor
from services.tooltip_manager import TooltipManager
from frameworks import FRAMEWORKS


class QueryEngine:
    """Main query engine with modular architecture"""
    
    def __init__(self):
        # Initialize configuration
        self.config = Config()
        
        # Initialize OpenAI client
        from openai import OpenAI
        self.client = OpenAI(api_key=self.config.openai_api_key)
        
        # Initialize services
        self.tooltip_manager = TooltipManager(self.config, self.client)
        self.answer_processor = AnswerProcessor()
        
        # Load models and data
        self._load_models()
        self._load_data()
        
        # Initialize tracking
        self.usage_metrics = {
            'total_queries': 0,
            'total_tokens': 0,
            'avg_response_time': 0,
            'quality_scores': [],
            'cost_estimate': 0.0
        }
    
    def _load_models(self):
        """Load embedding and NLP models"""
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
            print("✅ Loaded embedding model")
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            sys.exit(1)
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ Loaded NLP model")
        except Exception as e:
            print(f"❌ Error loading NLP model: {e}")
            sys.exit(1)
    
    def _load_data(self):
        """Load FAISS index and metadata"""
        try:
            self.index = faiss.read_index("vector_index.faiss")
            print("✅ Loaded FAISS index")
        except Exception as e:
            print(f"❌ Error loading FAISS index: {e}")
            sys.exit(1)
        
        try:
            with open("metadata.json", "r", encoding="utf-8") as f:
                metadata = json.load(f)
            self.documents = metadata["documents"]
            self.file_names = metadata.get("file_names", ["Unknown"] * len(self.documents))
            print("✅ Loaded document metadata")
        except Exception as e:
            print(f"❌ Error loading metadata: {e}")
            sys.exit(1)
    
    def process_query(self, query: str, user_id: Optional[str] = None) -> APIResponse:
        """Process a query and return structured response"""
        try:
            # Validate input
            if not query.strip():
                return APIResponse.error_response("Query cannot be empty")
            
            # Track start time
            start_time = time.time()
            
            # Search for relevant documents
            relevant_docs = self._search_documents(query)
            if not relevant_docs:
                return APIResponse.error_response("No relevant documents found")
            
            # Generate answer
            answer_data = self._generate_answer(query, relevant_docs, user_id)
            
            # Calculate metrics
            response_time = time.time() - start_time
            self._track_usage(query, response_time, answer_data.metadata.get("estimated_tokens", 0))
            
            # Return structured response
            return APIResponse.success_response(answer_data.to_dict())
            
        except Exception as e:
            return APIResponse.error_response(f"Error processing query: {str(e)}")
    
    def _search_documents(self, query: str) -> List[str]:
        """Search for relevant documents"""
        try:
            # Encode query
            query_embedding = self.embedding_model.encode([query])
            query_embedding = np.array(query_embedding).astype("float32")
            
            # Search FAISS index
            D, I = self.index.search(query_embedding, 5)
            top_indices = I[0]
            
            if len(top_indices) == 0 or top_indices[0] == -1:
                return []
            
            # Get relevant documents
            relevant_docs = []
            for idx in top_indices:
                if idx != -1:
                    relevant_docs.append(self.documents[idx])
            
            return relevant_docs
            
        except Exception as e:
            print(f"❌ Error searching documents: {e}")
            return []
    
    def _generate_answer(self, query: str, relevant_docs: List[str], user_id: Optional[str] = None) -> AnswerData:
        """Generate answer with tooltips and metadata"""
        # Combine context
        combined_context = self._smart_context_truncation(relevant_docs)
        
        # Generate personalized prompt
        personalized_instruction = self.config.get_personalized_instruction(user_id)
        prompt = f"{personalized_instruction}\n\nDocument excerpts:\n{combined_context}\n\nQuestion: {query}\n\nSynthesized Answer (use the required structure):"
        
        # Calculate optimal tokens
        optimal_tokens = self._calculate_optimal_tokens(len(query), len(combined_context))
        
        # Call OpenAI API
        response = self._robust_api_call(prompt, optimal_tokens)
        if not response:
            raise Exception("Failed to get response from OpenAI")
        
        content = response.choices[0].message.content
        answer = content.strip() if content is not None else ""
        
        # Process answer
        answer = self._process_answer(answer, query, combined_context)
        
        # Extract tooltips
        tooltips = self._extract_tooltips(answer, combined_context)
        
        # Create metadata
        metadata = {
            "sources": len(relevant_docs),
            "response_time": time.time(),
            "estimated_tokens": len(prompt.split()) + len(answer.split()),
            "context_length": len(combined_context),
            "user_id": user_id
        }
        
        return AnswerData(answer, tooltips, metadata)
    
    def _smart_context_truncation(self, docs: List[str], max_chars: int = 8000) -> str:
        """Smart context truncation with sentence boundaries"""
        if not docs:
            return ""
        
        # Score documents by relevance (simplified)
        scored_docs = []
        for i, doc in enumerate(docs):
            position_score = 1.0 / (i + 1)
            content_score = min(len(doc) / 1000, 2.0)
            total_score = position_score * content_score
            scored_docs.append((doc, total_score))
        
        # Sort by relevance
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Build context
        combined_context = ""
        for doc, score in scored_docs:
            remaining_chars = max_chars - len(combined_context)
            if remaining_chars <= 0:
                break
            
            if len(doc) > remaining_chars:
                truncated = doc[:remaining_chars]
                last_period = truncated.rfind('.')
                last_exclamation = truncated.rfind('!')
                last_question = truncated.rfind('?')
                
                break_point = max(last_period, last_exclamation, last_question)
                if break_point > remaining_chars * 0.7:
                    doc = doc[:break_point + 1]
                else:
                    doc = truncated + "..."
            
            if combined_context:
                combined_context += "\n\n---\n\n"
            combined_context += doc
        
        return combined_context
    
    def _calculate_optimal_tokens(self, query_length: int, context_length: int) -> int:
        """Calculate optimal token limit"""
        total_input = query_length + context_length
        base_tokens = self.config.openai_max_tokens
        
        if total_input > 6000:
            return min(800, base_tokens)
        elif total_input > 3000:
            return min(1200, base_tokens)
        else:
            return base_tokens
    
    def _robust_api_call(self, prompt: str, max_tokens: int, max_retries: int = 3) -> Optional[Any]:
        """Robust API call with retries"""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.config.openai_temperature,
                    max_tokens=max_tokens
                )
                return response
            except Exception as e:
                if attempt < max_retries - 1:
                    delay = 1.0 * (2 ** attempt)
                    print(f"⚠️ API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"   Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
                else:
                    print(f"❌ API call failed after {max_retries} attempts: {e}")
                    return None
        
        return None
    
    def _process_answer(self, answer: str, query: str, context: str) -> str:
        """Process and enhance answer"""
        # Remove names
        answer = self._remove_names(answer)
        
        # Highlight frameworks
        answer = self._highlight_frameworks(answer)
        
        # Improve flow
        answer = self._improve_strategic_thinking_flow(answer)
        
        return answer
    
    def _remove_names(self, text: str) -> str:
        """Remove personal names from text"""
        protected_variations = [
            "💬 Want to Go Deeper?",
            "Want to Go Deeper?",
            "Want to Go individual?"
        ]
        
        # Protect labels
        for i, variation in enumerate(protected_variations):
            text = text.replace(variation, f"<<PROTECTED_LABEL_{i}>>")
        
        # Remove names
        doc = self.nlp(text)
        result = []
        last_idx = 0
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                result.append(text[last_idx:ent.start_char])
                result.append("individual")
                last_idx = ent.end_char
        result.append(text[last_idx:])
        text = "".join(result)
        
        # Restore labels
        for i, variation in enumerate(protected_variations):
            text = text.replace(f"<<PROTECTED_LABEL_{i}>>", "💬 Want to Go Deeper?")
        
        return text
    
    def _highlight_frameworks(self, answer: str) -> str:
        """Highlight decision frameworks in answer"""
        def bold_with_tooltip(match):
            fw = match.group(0)
            key = fw.lower()
            explanation = FRAMEWORKS.get(key, "")
            if explanation:
                return f"**{fw}** ({explanation})"
            else:
                return f"**{fw}**"
        
        # Sort frameworks by length to avoid partial matches
        sorted_frameworks = sorted(FRAMEWORKS.keys(), key=len, reverse=True)
        for fw in sorted_frameworks:
            pattern = re.compile(rf'\b{re.escape(fw)}\b', re.IGNORECASE)
            answer = pattern.sub(bold_with_tooltip, answer)
        
        return answer
    
    def _improve_strategic_thinking_flow(self, answer: str) -> str:
        """Improve flow of Strategic Thinking Lens section"""
        strategic_pattern = r'(\*\*🧠 Strategic Thinking Lens.*?\*\*.*?)(\*\*📘|\*\*💬|$)'
        match = re.search(strategic_pattern, answer, re.DOTALL | re.IGNORECASE)
        
        if not match:
            return answer
        
        strategic_section = match.group(1)
        rest_of_answer = answer[match.end():]
        
        # Tool-focused openings to improve
        tool_openings = [
            (r'\*\*Decision trees?\*\* are best used when', 'When you\'re faced with multiple options and uncertainty, **decision trees** help you visualize possible outcomes and make more confident choices.'),
            (r'\*\*SWOT analysis\*\* is a framework', 'When you need to assess your situation comprehensively, **SWOT analysis** helps you identify strengths, weaknesses, opportunities, and threats.'),
            (r'\*\*Cost-benefit analysis\*\* involves', 'When weighing different options, **cost-benefit analysis** helps you systematically compare the pros and cons of each choice.')
        ]
        
        # Apply improvements
        improved_section = strategic_section
        for pattern, replacement in tool_openings:
            if re.search(pattern, improved_section, re.IGNORECASE):
                improved_section = re.sub(pattern, replacement, improved_section, flags=re.IGNORECASE)
                break
        
        return improved_section + rest_of_answer
    
    def _extract_tooltips(self, answer: str, context: str) -> Dict[str, str]:
        """Extract tooltips from answer and context"""
        all_concepts = set(FRAMEWORKS.keys())
        found = []
        tooltip_metadata = {}
        
        text_to_search = f"{answer}\n{context}"
        for concept in all_concepts:
            pattern = re.compile(rf'\b{re.escape(concept)}\b', re.IGNORECASE)
            if pattern.search(text_to_search):
                display_name = " ".join([w.capitalize() for w in concept.split()])
                found.append((concept, display_name))
        
        # Get tooltips
        for concept, display_name in sorted(found, key=lambda x: x[1]):
            tooltip_text, is_prebuilt, source_type = self.tooltip_manager.get_tooltip(concept, context)
            tooltip_metadata[display_name] = tooltip_text
        
        return tooltip_metadata
    
    def _track_usage(self, query: str, response_time: float, tokens_used: int):
        """Track usage metrics"""
        self.usage_metrics['total_queries'] += 1
        self.usage_metrics['total_tokens'] += tokens_used
        
        # Update average response time
        if self.usage_metrics['avg_response_time'] == 0:
            self.usage_metrics['avg_response_time'] = response_time
        else:
            self.usage_metrics['avg_response_time'] = (self.usage_metrics['avg_response_time'] + response_time) / 2
        
        # Estimate cost (GPT-3.5-turbo rates)
        input_cost = (tokens_used * 0.7) * 0.0015 / 1000
        output_cost = (tokens_used * 0.3) * 0.002 / 1000
        self.usage_metrics['cost_estimate'] += input_cost + output_cost
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage summary"""
        if self.usage_metrics['total_queries'] == 0:
            return {"message": "No queries processed yet"}
        
        quality_rate = sum(self.usage_metrics['quality_scores']) / len(self.usage_metrics['quality_scores']) * 100 if self.usage_metrics['quality_scores'] else 0
        
        return {
            'total_queries': self.usage_metrics['total_queries'],
            'total_tokens': self.usage_metrics['total_tokens'],
            'avg_response_time': self.usage_metrics['avg_response_time'],
            'quality_rate': f"{quality_rate:.1f}%",
            'estimated_cost': f"${self.usage_metrics['cost_estimate']:.4f}",
            'avg_tokens_per_query': self.usage_metrics['total_tokens'] / self.usage_metrics['total_queries'],
            'tooltip_stats': self.tooltip_manager.get_usage_stats()
        }


def main():
    """Main function for CLI usage"""
    print("🚀 Initializing GPTTutor Query Engine...")
    
    try:
        engine = QueryEngine()
        print("✅ Query engine is ready!")
        print("💡 This engine will synthesize answers from multiple relevant documents.")
        
        # CLI loop
        while True:
            try:
                query = input("\nAsk a question (or type 'exit' or 'stats'): ")
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Exiting. Goodbye!")
                break
            
            if query.strip().lower() == "exit":
                print("👋 Exiting. Goodbye!")
                break
            
            if query.strip().lower() == "stats":
                summary = engine.get_usage_summary()
                print(f"\n📊 Usage Statistics:")
                for key, value in summary.items():
                    print(f"   {key.replace('_', ' ').title()}: {value}")
                continue
            
            if not query.strip():
                print("⚠️ Please enter a non-empty question.")
                continue
            
            # Process query
            response = engine.process_query(query)
            
            if response.success:
                data = response.data
                print(f"\n🎯 Synthesized Answer:\n{data['answer']}")
                print(f"\n📊 Sources: {data['metadata']['sources']} documents synthesized")
                print(f"⏱️ Response time: {data['metadata']['response_time']:.2f}s")
                
                if data['tooltips']:
                    print("\n🔧 Tooltips:")
                    for name, tooltip in data['tooltips'].items():
                        print(f"   {name}: {tooltip}")
            else:
                print(f"❌ Error: {response.error}")
                
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main() 