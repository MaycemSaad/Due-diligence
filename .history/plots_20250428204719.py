import plotly.graph_objects as go

def create_price_sentiment_chart(price_df, social_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_df['timestamp'], y=price_df['price'], name='Price', line=dict(color='cyan')))
    fig.add_trace(go.Scatter(x=social_df['timestamp'], y=social_df['sentiment'], name='Sentiment', line=dict(color='magenta'), yaxis="y2"))
    fig.update_layout(
        template='plotly_dark',
        yaxis2=dict(overlaying='y', side='right'),
        title='Price vs Sentiment',
        hovermode='x unified'
    )
    return fig

def create_sentiment_heatmap(social_df):
    pivot = social_df.pivot_table(index='source', columns=social_df['timestamp'].dt.floor('5min'), values='sentiment', aggfunc='mean')
    fig = go.Figure(go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index, colorscale='RdYlGn'))
    fig.update_layout(template='plotly_dark', title="Sentiment Heatmap")
    return fig

def create_volume_correlation_chart(price_df, social_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=social_df['volume'], y=price_df['volume'], mode='markers'))
    fig.update_layout(template='plotly_dark', title="Volume Correlation")
    return fig

def create_source_impact_chart(social_df):
    fig = go.Figure()
    for source in social_df['source'].unique():
        fig.add_trace(go.Box(y=social_df[social_df['source']==source]['sentiment'], name=source))
    fig.update_layout(template='plotly_dark', title="Source Sentiment Distribution")
    return fig

def create_technical_indicators(price_df):
    price_df['SMA10'] = price_df['price'].rolling(10).mean()
    price_df['SMA20'] = price_df['price'].rolling(20).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_df['timestamp'], y=price_df['price'], name='Price'))
    fig.add_trace(go.Scatter(x=price_df['timestamp'], y=price_df['SMA10'], name='SMA 10'))
    fig.add_trace(go.Scatter(x=price_df['timestamp'], y=price_df['SMA20'], name='SMA 20'))
    fig.update_layout(template='plotly_dark', title="Technical Indicators")
    return fig
