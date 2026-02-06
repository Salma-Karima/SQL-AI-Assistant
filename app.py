import streamlit as st
import plotly.express as px
from database import DatabaseConnector
from query_generator import SQLQueryGenerator
from query_history import QueryHistory
from streamlit_option_menu import option_menu
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
from utils import load_css
import json

# Load external CSS
load_css('assets/styles.css')

# Page config
st.set_page_config(
    page_title="🤖 Your SQL AI Assistant",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    db = DatabaseConnector()
    query_gen = SQLQueryGenerator(model="gemma3:4b")
    history = QueryHistory()
    return db, query_gen, history

db, query_gen, history = init_components()


# Hero Section - BIGGER
st.markdown("""
<div style='text-align: center; padding: 3rem 0;'>
    <h1 style='font-size: 9rem; margin-bottom: 20px;color: #ff0000; '>🤖  Your SQL AI Assistant</h1>
    <p style='font-size: 2rem;color: #1C3FAA; font-weight: 600; opacity: 0.9;'>
        Transform natural language into powerful SQL queries
    </p>
</div>
""", unsafe_allow_html=True)

add_vertical_space(3)

# Sidebar with better design
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>📊 Control Panel</h2>", unsafe_allow_html=True)
    
    add_vertical_space(1)
    
    selected = option_menu(
        menu_title=None,
        options=["Query", "Schema", "History"],
        icons=["chat-dots", "database", "clock-history"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#13488A", "font-size": "20px"}, 
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin":"0px",
                "--hover-color": "rgba(76, 175, 80, 0.2)"
            },
            "nav-link-selected": {"background-color": "rgba(76, 175, 80, 0.3)"},
        }
    )
    
    add_vertical_space(2)
    
    if selected == "Schema":
        colored_header(
            label="Database Schema",
            description="Current database structure",
            color_name="green-70"
        )
        schema = db.get_schema()
        st.code(schema, language="sql")
    
    elif selected == "History":
        colored_header(
            label="Query History",
            description="Recent queries",
            color_name="blue-70"
        )
        recent_queries = history.get_history(limit=5)
        
        if recent_queries:
            for i, entry in enumerate(recent_queries):
                with st.expander(f"🕐 {entry['timestamp']}", expanded=False):
                    st.write(f"**Question:** {entry['question']}")
                    st.code(entry['sql_query'], language="sql")
                    status_emoji = "✅" if entry['status'] == "SUCCESS" else "❌"
                    st.caption(f"{status_emoji} {entry['status']} | Results: {entry['results_count']}")
        else:
            st.info("No queries yet. Start asking questions!")
        
        add_vertical_space(1)
        if st.button("🗑️ Clear History", use_container_width=True):
            history.clear_history()
            st.rerun()

# Main content
if selected == "Query":
    # Question input - BIG
    question = st.text_input(
        "🗣️ Ask your question:",
        placeholder="e.g., Show me total sales by product category",
        key="question_input"
    )
    
    add_vertical_space(2)
    
    # Action buttons - BIGGER
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    
    with col1:
        generate_btn = st.button("🚀 Generate", type="primary", use_container_width=True)
    
    with col2:
        optimize_btn = st.button("⚡ Optimize", use_container_width=True)
    
    add_vertical_space(3)
    
    if generate_btn and question:
        schema = db.get_schema()
        
        with st.spinner("🤔 Generating SQL query..."):
            sql_query = query_gen.generate_query(question, schema)
            
            colored_header(
                label="Generated SQL Query",
                description="AI-powered query generation",
                color_name="green-70"
            )
            
            st.code(sql_query, language="sql")
            
            with st.spinner("⚙️ Executing query..."):
                df, error = db.execute_query(sql_query)
            
            if error:
                st.error(f"❌ Query Error: {error}")
                history.add_query(question, sql_query, "ERROR", 0)
            else:
                st.success(f"✅ Query executed successfully! Found {len(df)} results.")
                history.add_query(question, sql_query, "SUCCESS", len(df))
                
                add_vertical_space(2)
                
                colored_header(
                    label="Results",
                    description=f"{len(df)} rows returned",
                    color_name="blue-70"
                )
                
                st.dataframe(df, use_container_width=True, height=400)
                
                # Visualization
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                
                if len(numeric_cols) >= 1 and len(df) > 1:
                    add_vertical_space(2)
                    
                    colored_header(
                        label="Visualization",
                        description="Interactive data charts",
                        color_name="violet-70"
                    )
                    
                    chart_col1, chart_col2 = st.columns([1, 4])
                    
                    with chart_col1:
                        chart_type = st.radio(
                            "Chart Type:",
                            ["📊 Bar", "📈 Line", "🥧 Pie"],
                            label_visibility="collapsed"
                        )
                    
                    with chart_col2:
                        if len(df.columns) >= 2:
                            x_col = df.columns[0]
                            y_col = numeric_cols[0]
                            
                            if "Bar" in chart_type:
                                fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}",
                                           color_discrete_sequence=["#2F80FF"])
                            elif "Line" in chart_type:
                                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}",
                                            color_discrete_sequence=["#2F80FF"])
                            else:
                                fig = px.pie(df, names=x_col, values=y_col, title=f"{y_col} Distribution",
                                           color_discrete_sequence=px.colors.sequential.Blues)
                            
                            fig.update_layout(
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font_color='#1C3FAA',
                                font_size=16
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                
                # Download button
                add_vertical_space(2)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=csv,
                    file_name="query_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    if optimize_btn and 'sql_query' in locals():
        with st.spinner("⚡ Analyzing query..."):
            suggestions = query_gen.optimize_query(sql_query)
            st.info(suggestions)
    
    # Example questions - VERTICAL LAYOUT (ONE COLUMN)
    add_vertical_space(4)
    
    colored_header(
        label="💡 Example Questions",
        description="Try these sample queries",
        color_name="orange-70"
    )
    
    add_vertical_space(1)
    
    examples = [
        "Show me total sales for each product",
        "Which customers spent the most money?",
        "What are the top 3 selling products?",
        "Show me sales from last month",
        "Which country has the most customers?",
        "What's the average order value by product category?"
    ]
    
    # Display examples VERTICALLY (one column, bigger)
    for example in examples:
        st.markdown(f"""
        <div class='glass-card'>
            <p>💬 {example}</p>
        </div>
        """, unsafe_allow_html=True)