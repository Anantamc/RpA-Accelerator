import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from config import LEVELS, STATUS_OPTIONS, ACTIVITY_TYPES, SENTIMENT_MIN, SENTIMENT_MAX, SOCIAL_METRICS

def generate_partners(num_partners=30):
    data = []
    data.append({
        'partner_id': 1,
        'name': 'Root Distributor',
        'level': 'Distributor',
        'parent_id': None,
        'join_date': (datetime.now() - timedelta(days=random.randint(100, 1000))).strftime('%Y-%m-%d'),
        'status': random.choice(STATUS_OPTIONS),
        'posts': random.randint(10, 200),
        'shares': random.randint(20, 500),
        'sentiment': round(random.uniform(SENTIMENT_MIN, SENTIMENT_MAX), 2),
        'advocacy_score': random.randint(1, 100),
        'engagement': random.randint(1, 100),
        'total_revenue': round(random.uniform(10000, 100000), 2)
    })
    for i in range(2, num_partners + 1):
        level = random.choices(LEVELS, weights=[0.2, 0.5, 0.3])[0]
        parent_candidates = [d for d in data if LEVELS.index(d['level']) < LEVELS.index(level)]
        parent = random.choice(parent_candidates) if parent_candidates else data[0]
        data.append({
            'partner_id': i,
            'name': f'Partner {i}',
            'level': level,
            'parent_id': parent['partner_id'],
            'join_date': (datetime.now() - timedelta(days=random.randint(1, 900))).strftime('%Y-%m-%d'),
            'status': random.choice(STATUS_OPTIONS),
            'posts': random.randint(0, 200),
            'shares': random.randint(0, 500),
            'sentiment': round(random.uniform(SENTIMENT_MIN, SENTIMENT_MAX), 2),
            'advocacy_score': random.randint(1, 100),
            'engagement': random.randint(1, 100),
            'total_revenue': round(random.uniform(1000, 50000), 2)
        })
    return pd.DataFrame(data)

def generate_sales(partners, num_days=90):
    sales = []
    for _, p in partners.iterrows():
        # Generate a realistic sales pattern over time
        num_transactions = random.randint(10, 60)  # More transactions for longer time period
        for _ in range(num_transactions):
            date = datetime.now() - timedelta(days=random.randint(0, num_days))
            revenue = round(random.uniform(100, 2000), 2)
            # Add transaction ID and product info for more detailed reporting
            sales.append({
                'partner_id': p['partner_id'],
                'date': date.strftime('%Y-%m-%d'),
                'revenue': revenue,
                'transaction_id': f"TX-{random.randint(10000, 99999)}",
                'product': f"Product-{random.randint(1, 10)}"
            })
    return pd.DataFrame(sales)

def generate_activity(partners, num_days=90):
    activity = []
    for _, p in partners.iterrows():
        # Generate more activity data with varied types
        for _ in range(random.randint(20, 100)):
            date = datetime.now() - timedelta(days=random.randint(0, num_days))
            activity_type = random.choice(ACTIVITY_TYPES)
            activity.append({
                'partner_id': p['partner_id'],
                'date': date.strftime('%Y-%m-%d'),
                'activity_type': activity_type,
                'duration_minutes': random.randint(5, 120) if activity_type in ['Call', 'Meeting', 'Training'] else None
            })
    return pd.DataFrame(activity)

def generate_social_activity(partners, num_days=90):
    """Generate daily social media and digital engagement metrics for each partner"""
    social_data = []
    
    # Generate daily data for each partner
    for _, p in partners.iterrows():
        # Set base metrics for this partner (some partners are more active than others)
        base_posts = random.randint(0, 3)
        base_shares = random.randint(0, 5)
        base_sentiment_trend = random.uniform(-0.01, 0.01)  # Slight trend up or down
        base_advocacy = random.randint(30, 80)
        
        # Generate daily metrics with realistic patterns
        for day in range(num_days):
            date = datetime.now() - timedelta(days=num_days-day)
            
            # Add some randomness but maintain a pattern
            posts = max(0, int(np.random.poisson(base_posts)))
            shares = max(0, int(np.random.poisson(base_shares)))
            
            # Sentiment fluctuates but follows a trend
            sentiment = min(SENTIMENT_MAX, max(SENTIMENT_MIN, 
                        p['sentiment'] + (base_sentiment_trend * day/10) + random.uniform(-0.1, 0.1)))
                        
            # Advocacy score changes more slowly
            advocacy_score = min(100, max(1, base_advocacy + random.randint(-2, 2)))
            
            # Reviews are less frequent
            reviews = 1 if random.random() < 0.1 else 0
            
            social_data.append({
                'partner_id': p['partner_id'],
                'date': date.strftime('%Y-%m-%d'),
                'posts': posts,
                'shares': shares,
                'sentiment': round(sentiment, 2),
                'advocacy_score': advocacy_score,
                'reviews': reviews
            })
    
    return pd.DataFrame(social_data)
