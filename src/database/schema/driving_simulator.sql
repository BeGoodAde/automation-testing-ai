-- Enhanced Database Schema for Driving Simulator Analysis
-- Created by Adelaja Isreal Bolarinwa

-- Create database (run this separately in psql)
-- CREATE DATABASE driving_sim;

-- Reaction logs table (your original requirement)
CREATE TABLE IF NOT EXISTS reaction_logs (
    id SERIAL PRIMARY KEY,
    participant_id VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    obstacle_time TIMESTAMP NOT NULL,
    brake_time TIMESTAMP NOT NULL,
    reaction_time_ms INTEGER NOT NULL,
    scenario VARCHAR(100) NOT NULL,
    error BOOLEAN DEFAULT FALSE,
    fatigue_level INTEGER CHECK (fatigue_level BETWEEN 1 AND 10),
    session_duration INTEGER, -- in minutes
    weather_condition VARCHAR(50),
    traffic_density VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced simulator sessions table
CREATE TABLE IF NOT EXISTS simulator_sessions (
    session_id UUID PRIMARY KEY,
    participant_id VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    scenario_type VARCHAR(50) NOT NULL,
    weather_conditions VARCHAR(50),
    traffic_density VARCHAR(20),
    fatigue_level INTEGER CHECK (fatigue_level BETWEEN 1 AND 10),
    total_obstacles INTEGER DEFAULT 0,
    successful_reactions INTEGER DEFAULT 0,
    average_reaction_time DECIMAL(6,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    session_id UUID REFERENCES simulator_sessions(session_id),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    speed DECIMAL(5,2),
    acceleration DECIMAL(5,2),
    braking_force DECIMAL(5,2),
    steering_angle DECIMAL(6,2),
    lane_position DECIMAL(5,2),
    collision_detected BOOLEAN DEFAULT FALSE,
    distance_traveled DECIMAL(8,2)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_reaction_logs_participant ON reaction_logs(participant_id);
CREATE INDEX IF NOT EXISTS idx_reaction_logs_scenario ON reaction_logs(scenario);
CREATE INDEX IF NOT EXISTS idx_reaction_logs_timestamp ON reaction_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_sessions_participant ON simulator_sessions(participant_id);
CREATE INDEX IF NOT EXISTS idx_metrics_session_id ON performance_metrics(session_id);

-- Views for analysis
CREATE OR REPLACE VIEW participant_performance AS
SELECT 
    participant_id,
    COUNT(*) as total_trials,
    AVG(reaction_time_ms) as avg_reaction_time,
    MIN(reaction_time_ms) as best_reaction_time,
    MAX(reaction_time_ms) as worst_reaction_time,
    STDDEV(reaction_time_ms) as reaction_time_stddev,
    SUM(CASE WHEN error THEN 1 ELSE 0 END) as error_count,
    (SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100) as error_rate
FROM reaction_logs
GROUP BY participant_id;

CREATE OR REPLACE VIEW scenario_analysis AS
SELECT 
    scenario,
    COUNT(*) as total_trials,
    AVG(reaction_time_ms) as avg_reaction_time,
    SUM(CASE WHEN error THEN 1 ELSE 0 END) as total_errors,
    (SUM(CASE WHEN error THEN 1 ELSE 0 END)::float / COUNT(*) * 100) as error_rate
FROM reaction_logs
GROUP BY scenario
ORDER BY avg_reaction_time DESC;