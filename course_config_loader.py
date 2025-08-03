#!/usr/bin/env python3
"""
Course Configuration Loader
Validates and loads course-specific configurations
"""
import json
import os
from typing import Dict, Any, List

def load_course_config(course_id: str) -> Dict[str, Any]:
    """
    Load complete course configuration from file
    
    Args:
        course_id: Course identifier (e.g., 'decision', 'marketing')
        
    Returns:
        Complete course configuration dictionary
        
    Raises:
        ValueError: If course configuration is missing or invalid
    """
    course_path = os.path.join("courses", course_id)
    config_path = os.path.join(course_path, "course_config.json")
    
    if not os.path.exists(config_path):
        raise ValueError(f"Course configuration not found: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in course config {config_path}: {e}")
    
    # Validate required fields
    validate_course_config(config)
    
    return config

def validate_course_config(config: Dict[str, Any]) -> bool:
    """
    Validate course configuration completeness
    
    Args:
        config: Course configuration dictionary
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    # Required top-level fields
    required_fields = [
        "course_id", "name", "version", "domains", 
        "application_fields", "entity_types"
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field '{field}' in course config")
    
    # Validate domains structure
    if not isinstance(config['domains'], dict):
        raise ValueError("'domains' must be a dictionary")
    
    for domain_name, domain_config in config['domains'].items():
        if not isinstance(domain_config, dict):
            raise ValueError(f"Domain '{domain_name}' config must be a dictionary")
        
        if 'keywords' not in domain_config:
            raise ValueError(f"Domain '{domain_name}' missing 'keywords' field")
        
        if 'concepts' not in domain_config:
            raise ValueError(f"Domain '{domain_name}' missing 'concepts' field")
        
        if not isinstance(domain_config['keywords'], list):
            raise ValueError(f"Domain '{domain_name}' keywords must be a list")
        
        if not isinstance(domain_config['concepts'], list):
            raise ValueError(f"Domain '{domain_name}' concepts must be a list")
    
    # Validate application fields
    if not isinstance(config['application_fields'], list):
        raise ValueError("'application_fields' must be a list")
    
    if len(config['application_fields']) == 0:
        raise ValueError("'application_fields' cannot be empty")
    
    # Validate entity types
    if not isinstance(config['entity_types'], dict):
        raise ValueError("'entity_types' must be a dictionary")
    
    for entity_type, entity_descriptions in config['entity_types'].items():
        if not isinstance(entity_descriptions, list):
            raise ValueError(f"Entity type '{entity_type}' descriptions must be a list")
    
    return True

def get_available_courses() -> List[str]:
    """
    Get list of available course IDs
    
    Returns:
        List of course IDs
    """
    courses_dir = "courses"
    if not os.path.exists(courses_dir):
        return []
    
    available_courses = []
    for item in os.listdir(courses_dir):
        course_path = os.path.join(courses_dir, item)
        config_path = os.path.join(course_path, "course_config.json")
        
        if os.path.isdir(course_path) and os.path.exists(config_path):
            available_courses.append(item)
    
    return available_courses

def test_course_configurations():
    """
    Test that all course configurations are valid
    """
    print("🔍 TESTING COURSE CONFIGURATIONS")
    print("=" * 50)
    
    available_courses = get_available_courses()
    
    if not available_courses:
        print("❌ No course configurations found")
        return False
    
    all_valid = True
    
    for course_id in available_courses:
        try:
            config = load_course_config(course_id)
            print(f"✅ Course '{course_id}' configuration loaded successfully")
            print(f"   Name: {config['name']}")
            print(f"   Version: {config['version']}")
            print(f"   Domains: {list(config['domains'].keys())}")
            print(f"   Application Fields: {len(config['application_fields'])}")
            print(f"   Entity Types: {len(config['entity_types'])}")
            
            # Validate completeness
            validate_course_config(config)
            print(f"✅ Course '{course_id}' configuration validated")
            
        except Exception as e:
            print(f"❌ Course '{course_id}' configuration failed: {e}")
            all_valid = False
    
    if all_valid:
        print(f"\n✅ All {len(available_courses)} course configurations are valid")
    else:
        print(f"\n❌ Some course configurations have issues")
    
    return all_valid

def get_course_domains(course_id: str) -> List[str]:
    """
    Get list of domains for a specific course
    
    Args:
        course_id: Course identifier
        
    Returns:
        List of domain names
    """
    config = load_course_config(course_id)
    return list(config['domains'].keys())

def get_course_keywords(course_id: str, domain: str) -> List[str]:
    """
    Get keywords for a specific domain in a course
    
    Args:
        course_id: Course identifier
        domain: Domain name
        
    Returns:
        List of keywords
    """
    config = load_course_config(course_id)
    
    if domain not in config['domains']:
        raise ValueError(f"Domain '{domain}' not found in course '{course_id}'")
    
    return config['domains'][domain]['keywords']

def get_course_concepts(course_id: str, domain: str) -> List[str]:
    """
    Get concepts for a specific domain in a course
    
    Args:
        course_id: Course identifier
        domain: Domain name
        
    Returns:
        List of concepts
    """
    config = load_course_config(course_id)
    
    if domain not in config['domains']:
        raise ValueError(f"Domain '{domain}' not found in course '{course_id}'")
    
    return config['domains'][domain]['concepts']

if __name__ == "__main__":
    # Test course configurations
    test_course_configurations() 