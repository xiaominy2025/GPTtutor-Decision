import React from 'react';

interface FollowUpPromptsProps {
  followUpPrompts?: string[];
  className?: string;
}

export const FollowUpPrompts: React.FC<FollowUpPromptsProps> = ({ 
  followUpPrompts = [], 
  className = '' 
}) => {
  // Clean and filter the prompts
  const cleanPrompts = followUpPrompts
    .map(p => p.trim())
    .filter(p => p.length > 0)
    .map(prompt => {
      // Remove any existing bullet points or dashes
      let cleaned = prompt.replace(/^[-•*○\s]+/, '').trim();
      
      // Remove any nested formatting like "• -" or "○ -"
      cleaned = cleaned.replace(/^[•○]\s*[-•*○\s]*/, '').trim();
      
      return cleaned;
    })
    .filter(p => p.length > 0);

  if (cleanPrompts.length === 0) {
    return null;
  }

  return (
    <div className={`follow-up-prompts ${className}`}>
      <h3 className="text-lg font-semibold mb-3 text-gray-800">
        Follow-up Prompts
      </h3>
      <ul className="space-y-2">
        {cleanPrompts.map((prompt, index) => (
          <li 
            key={index} 
            className="flex items-start space-x-2 text-gray-700"
          >
            <span className="text-blue-600 font-medium mt-0.5">•</span>
            <span className="flex-1">{prompt}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Alternative version with custom bullet styling
export const FollowUpPromptsStyled: React.FC<FollowUpPromptsProps> = ({ 
  followUpPrompts = [], 
  className = '' 
}) => {
  // Clean and filter the prompts
  const cleanPrompts = followUpPrompts
    .map(p => p.trim())
    .filter(p => p.length > 0)
    .map(prompt => {
      // Remove any existing bullet points, dashes, or nested formatting
      let cleaned = prompt
        .replace(/^[-•*○\s]+/, '') // Remove leading bullets/dashes
        .replace(/^[•○]\s*[-•*○\s]*/, '') // Remove nested formatting like "• -"
        .trim();
      
      return cleaned;
    })
    .filter(p => p.length > 0);

  if (cleanPrompts.length === 0) {
    return null;
  }

  return (
    <div className={`follow-up-prompts ${className}`}>
      <h3 className="text-lg font-semibold mb-3 text-gray-800 border-b border-gray-200 pb-2">
        Follow-up Prompts
      </h3>
      <ul className="space-y-3">
        {cleanPrompts.map((prompt, index) => (
          <li 
            key={index} 
            className="relative pl-6 text-gray-700 leading-relaxed"
          >
            {/* Custom bullet point */}
            <div className="absolute left-0 top-2 w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>{prompt}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Version that handles markdown parsing
export const FollowUpPromptsMarkdown: React.FC<FollowUpPromptsProps> = ({ 
  followUpPrompts = [], 
  className = '' 
}) => {
  // Clean and filter the prompts
  const cleanPrompts = followUpPrompts
    .map(p => p.trim())
    .filter(p => p.length > 0)
    .map(prompt => {
      // Handle various markdown bullet formats
      let cleaned = prompt
        .replace(/^[-•*○\s]+/, '') // Remove leading bullets/dashes
        .replace(/^[•○]\s*[-•*○\s]*/, '') // Remove nested formatting
        .replace(/^\d+\.\s*/, '') // Remove numbered lists
        .trim();
      
      return cleaned;
    })
    .filter(p => p.length > 0);

  if (cleanPrompts.length === 0) {
    return null;
  }

  return (
    <div className={`follow-up-prompts ${className}`}>
      <h3 className="text-lg font-semibold mb-3 text-gray-800">
        Follow-up Prompts
      </h3>
      <ul className="space-y-2 list-none">
        {cleanPrompts.map((prompt, index) => (
          <li 
            key={index} 
            className="flex items-start space-x-3 text-gray-700"
          >
            <span className="text-blue-600 font-bold text-lg leading-none">•</span>
            <span className="flex-1 leading-relaxed">{prompt}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

// Hook for processing follow-up prompts
export const useFollowUpPrompts = (followUpPrompts?: string[]) => {
  const processedPrompts = React.useMemo(() => {
    if (!followUpPrompts || followUpPrompts.length === 0) {
      return [];
    }

    return followUpPrompts
      .map(p => p.trim())
      .filter(p => p.length > 0)
      .map(prompt => {
        // Remove any bullet point formatting and clean the text
        let cleaned = prompt
          .replace(/^[-•*○\s]+/, '') // Remove leading bullets/dashes
          .replace(/^[•○]\s*[-•*○\s]*/, '') // Remove nested formatting
          .replace(/^\d+\.\s*/, '') // Remove numbered lists
          .trim();
        
        return cleaned;
      })
      .filter(p => p.length > 0);
  }, [followUpPrompts]);

  return processedPrompts;
};

export default FollowUpPrompts; 