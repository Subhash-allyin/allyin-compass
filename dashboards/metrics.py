import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

class MetricsDashboard:
    def __init__(self):
        self.feedback_file = Path("feedback/feedback.jsonl")
        self.query_log_file = Path("logs/query_log.jsonl")
    
    def load_logs(self):
        """Load query logs"""
        if not self.query_log_file.exists():
            return []
        
        logs = []
        try:
            with open(self.query_log_file, 'r') as f:
                for line in f:
                    logs.append(json.loads(line.strip()))
        except:
            pass
        return logs
    
    def load_feedback(self):
        """Load feedback logs"""
        if not self.feedback_file.exists():
            return []
        
        feedback = []
        try:
            with open(self.feedback_file, 'r') as f:
                for line in f:
                    feedback.append(json.loads(line.strip()))
        except:
            pass
        return feedback
    
    def get_summary_metrics(self):
        """Get basic metrics"""
        logs = self.load_logs()
        feedback = self.load_feedback()
        
        total_queries = len(logs)
        
        # Calculate averages
        if logs:
            avg_response_time = sum(log.get('execution_time', 0) for log in logs) / len(logs)
            
            # Today's queries
            today = datetime.now().date()
            queries_today = sum(1 for log in logs 
                              if datetime.fromisoformat(log['timestamp']).date() == today)
        else:
            avg_response_time = 0
            queries_today = 0
        
        # Satisfaction rate
        satisfaction_rate = 0
        if feedback:
            positive = sum(1 for f in feedback if f.get('rating', 0) > 0)
            satisfaction_rate = positive / len(feedback)
        
        return {
            "total_queries": total_queries,
            "queries_today": queries_today, 
            "avg_response_time": avg_response_time,
            "satisfaction_rate": satisfaction_rate
        }
    
    def display_live_dashboard(self):
        """Display simple dashboard in sidebar"""
        # Summary metrics
        metrics = self.get_summary_metrics()
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Total Queries", metrics["total_queries"])
            st.metric("👍 Positive", len([f for f in self.load_feedback() if f.get('rating', 0) > 0]))
        
        with col2:
            st.metric("Avg Response", f"{metrics['avg_response_time']:.1f}s")
            st.metric("Satisfaction", f"{metrics['satisfaction_rate']:.1%}")
        
        # Show charts toggle
        if st.sidebar.checkbox("📈 Show Charts"):
            self._display_charts()
    
    def _display_charts(self):
        """Display simple charts"""
        logs = self.load_logs()
        
        if not logs:
            st.sidebar.info("No data to chart yet")
            return
        
        # 1. Queries per day
        daily_counts = defaultdict(int)
        for log in logs:
            try:
                date = datetime.fromisoformat(log['timestamp']).date()
                daily_counts[date] += 1
            except:
                continue
        
        if daily_counts:
            st.sidebar.subheader("📊 Queries per Day")
            df_daily = pd.DataFrame([
                {"Date": str(date), "Queries": count} 
                for date, count in sorted(daily_counts.items())
            ]).set_index("Date")
            st.sidebar.line_chart(df_daily)
        
        # 2. Tool usage frequency
        tool_counts = Counter()
        for log in logs:
            for tool in log.get('tools_used', []):
                tool_counts[tool] += 1
        
        if tool_counts:
            st.sidebar.subheader("🔧 Tool Usage")
            df_tools = pd.DataFrame([
                {"Tool": tool, "Usage": count}
                for tool, count in tool_counts.items()
            ]).set_index("Tool")
            st.sidebar.bar_chart(df_tools)
        
        # 3. Response times (last 10 queries)
        recent_logs = logs[-10:] if len(logs) > 10 else logs
        response_times = [log.get('execution_time', 0) for log in recent_logs]
        
        if response_times:
            st.sidebar.subheader("⏱️ Response Times")
            df_times = pd.DataFrame({
                "Response Time (s)": response_times
            })
            st.sidebar.line_chart(df_times)