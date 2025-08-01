"""
Web Dashboard for Driving Simulator Analysis
Provides real-time analytics and data visualization
Created by Adelaja Isreal Bolarinwa
"""

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root / 'src' / 'database' / 'python_integration'))

from simulator_db import DrivingSimulatorDB

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize database connection
db = DrivingSimulatorDB()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Get overall statistics"""
    try:
        db.connect()
        
        # Get basic stats
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(*) as total_records,
                COUNT(DISTINCT participant_id) as total_participants,
                AVG(reaction_time_ms) as avg_reaction_time,
                (SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100) as error_rate
            FROM reaction_logs
        """)
        
        stats = cursor.fetchone()
        cursor.close()
        
        return jsonify({
            'total_records': stats[0] or 0,
            'total_participants': stats[1] or 0,
            'avg_reaction_time': round(float(stats[2] or 0), 2),
            'error_rate': round(float(stats[3] or 0), 2)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/api/reaction-times')
def get_reaction_times():
    """Get reaction time data for visualization"""
    try:
        db.connect()
        
        query = """
        SELECT participant_id, reaction_time_ms, scenario, error, 
               weather_condition, traffic_density, timestamp
        FROM reaction_logs 
        ORDER BY timestamp DESC 
        LIMIT 1000
        """
        
        df = pd.read_sql(query, db.conn)
        
        return jsonify({
            'data': df.to_dict('records'),
            'columns': df.columns.tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/api/scenario-analysis')
def get_scenario_analysis():
    """Get scenario-based analysis"""
    try:
        db.connect()
        
        query = """
        SELECT 
            scenario,
            COUNT(*) as total_trials,
            AVG(reaction_time_ms) as avg_reaction_time,
            (SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100) as error_rate
        FROM reaction_logs
        GROUP BY scenario
        ORDER BY avg_reaction_time DESC
        """
        
        df = pd.read_sql(query, db.conn)
        
        # Create plotly chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['scenario'],
            y=df['avg_reaction_time'],
            name='Avg Reaction Time (ms)',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title='Average Reaction Time by Scenario',
            xaxis_title='Scenario',
            yaxis_title='Reaction Time (ms)',
            template='plotly_white'
        )
        
        chart_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            'chart': chart_json,
            'data': df.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/api/participant/<participant_id>')
def get_participant_data(participant_id):
    """Get specific participant's performance data"""
    try:
        db.connect()
        
        query = """
        SELECT reaction_time_ms, scenario, error, timestamp,
               weather_condition, traffic_density, fatigue_level
        FROM reaction_logs 
        WHERE participant_id = %s
        ORDER BY timestamp
        """
        
        df = pd.read_sql(query, db.conn, params=[participant_id])
        
        if df.empty:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Calculate trends
        df['moving_avg'] = df['reaction_time_ms'].rolling(window=5).mean()
        
        return jsonify({
            'participant_id': participant_id,
            'total_trials': len(df),
            'avg_reaction_time': df['reaction_time_ms'].mean(),
            'error_rate': (df['error'].sum() / len(df) * 100),
            'trend_data': df.to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/api/generate-data', methods=['POST'])
def generate_sample_data():
    """Generate sample data endpoint"""
    try:
        data = request.get_json()
        num_participants = data.get('participants', 10)
        trials_per_participant = data.get('trials', 50)
        
        db.connect()
        db.generate_sample_data(num_participants, trials_per_participant)
        
        return jsonify({
            'success': True,
            'message': f'Generated data for {num_participants} participants with {trials_per_participant} trials each'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/api/export')
def export_data():
    """Export data to Excel"""
    try:
        db.connect()
        
        # Create temporary file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'driving_simulator_export_{timestamp}.xlsx'
        filepath = project_root / 'data' / 'output' / filename
        
        # Ensure output directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        db.export_to_excel(str(filepath))
        
        return send_file(
            str(filepath),
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.disconnect()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        db.connect()
        cursor = db.conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        db.disconnect()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'disconnected',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)