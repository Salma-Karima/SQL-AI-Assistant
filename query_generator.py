from langchain_ollama import OllamaLLM
from datetime import datetime

class SQLQueryGenerator:
    def __init__(self, model="gemma3:4b"):
        self.llm = OllamaLLM(model=model)
    
    def generate_query(self, question, schema, chat_history=None):
        """Generate SQL query from natural language"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        prompt = f"""You are an expert SQL query generator. Generate ONLY the SQL query, nothing else.

DATABASE SCHEMA:
{schema}

IMPORTANT RULES:
1. Generate ONLY valid SQLite syntax
2. Use proper JOIN syntax when needed
3. Today's date is {current_date}
4. For "last month" queries, use: date('now', '-1 month')
5. Return ONLY the SQL query, no explanations
6. Use GROUP BY for aggregations
7. Use proper table aliases for readability

USER QUESTION: {question}

SQL QUERY:"""

        sql_query = self.llm.invoke(prompt).strip()
        
        # Clean up common issues
        sql_query = sql_query.replace("```sqlite", "").replace("```", "").strip()
        
        return sql_query
    
    def optimize_query(self, query):
        """Suggest query optimizations"""
        
        prompt = f"""Analyze this SQL query and provide 2-3 brief optimization suggestions:

{query}

Suggestions:"""
        
        suggestions = self.llm.invoke(prompt).strip()
        return suggestions
print("done")