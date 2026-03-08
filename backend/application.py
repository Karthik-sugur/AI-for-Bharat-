"""
AWS Elastic Beanstalk Entry Point
This file is the entry point for EB deployment
"""

from app.main import app

# Elastic Beanstalk looks for 'application' object
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=5000)
