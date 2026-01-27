#!/usr/bin/env python3
"""
Minimal Lambda Handler for Testing - No External Dependencies
"""

import json
from datetime import datetime

def lambda_handler(event, context):
    """
    Minimal Lambda handler for testing
    """
    print("🚀 Minimal Lambda Handler Starting")
    print(f"Event: {event}")
    
    try:
        # Basic response with CORS headers
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "https://engentlabs.com",
                "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type,Authorization",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "data": {
                    "status": "healthy",
                    "version": "V1.6.6.6",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "status": "success",
                "version": "V1.6.6.6",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "https://engentlabs.com",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "data": {"error": str(e)},
                "status": "error",
                "version": "V1.6.6.6",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
        }
