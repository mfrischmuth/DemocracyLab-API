from flask import Blueprint, request

from app import app

@app.route('/')
def index():
    return "ROOT API"
