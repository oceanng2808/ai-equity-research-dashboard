"""
Module 3: Visualization - Fixed for single chart without duplicate volume
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import traceback


class DataVisualizer:
    """Generates professional interactive charts"""
    
    def __init__(self):
        self.colors = {
            'gold': '#C9A03D',
            'blue': '#2D7FF9',
            'green': '#00C49A',
            'red': '#FF6B6B',
            'orange': '#FF8C42',
            'white': '#FFFFFF'
        }
    
    def create_interactive_price_chart(self, df: pd.DataFrame, ticker: str) -> str:
        """Create price chart with volume as secondary y-axis (single chart)"""
        try:
            if df is None or df.empty:
                return json.dumps({'error': 'No data available'})
            
            # Use last 180 days for cleaner view
            plot_df = df.tail(180).copy()
            plot_df = plot_df.reset_index()
            
            # Ensure we have Date column
            if 'Date' not in plot_df.columns:
                if 'index' in plot_df.columns:
                    plot_df = plot_df.rename(columns={'index': 'Date'})
                else:
                    plot_df['Date'] = pd.date_range(end=pd.Timestamp.now(), periods=len(plot_df), freq='D')
            
            dates = plot_df['Date'].dt.strftime('%Y-%m-%d').tolist()
            prices = plot_df['Close'].astype(float).tolist()
            volumes = plot_df['Volume'].astype(float).tolist()
            
            # Create figure with secondary y-axis for volume
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add price line
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=prices,
                    mode='lines',
                    name=f'{ticker} Price',
                    line=dict(color=self.colors['blue'], width=2),
                    fill='tozeroy',
                    fillcolor='rgba(45, 127, 249, 0.1)',
                    hovertemplate='<b>Date</b>: %{x}<br><b>Price</b>: $%{y:.2f}<extra></extra>'
                ),
                secondary_y=False
            )
            
            # Add volume as bars on secondary y-axis
            volume_colors = [
                self.colors['green'] if plot_df['Close'].iloc[i] >= plot_df['Open'].iloc[i] 
                else self.colors['red'] 
                for i in range(len(plot_df))
            ]
            
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=volumes,
                    name='Volume',
                    marker=dict(color=volume_colors, opacity=0.4),
                    hovertemplate='<b>Volume</b>: %{y:,.0f}<extra></extra>'
                ),
                secondary_y=True
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text=f'{ticker} - Price & Volume',
                    font=dict(size=16, color=self.colors['white'], family='Playfair Display'),
                    x=0.05
                ),
                height=500,
                hovermode='x unified',
                plot_bgcolor='#161B22',
                paper_bgcolor='#161B22',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color=self.colors['white'], size=10),
                    bgcolor='rgba(22, 27, 34, 0.8)',
                    bordercolor=self.colors['gold'],
                    borderwidth=1
                ),
                xaxis=dict(
                    title='Date',
                    gridcolor='#2D3748',
                    tickfont=dict(color=self.colors['white'], size=10),
                    tickangle=-45,
                    rangeslider=dict(visible=True, thickness=0.05)
                )
            )
            
            # Update y-axes
            fig.update_yaxes(
                title_text="Price (USD)",
                tickprefix='$',
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                title_font=dict(color=self.colors['white']),
                secondary_y=False
            )
            
            fig.update_yaxes(
                title_text="Volume",
                tickformat=',.0f',
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                title_font=dict(color=self.colors['white']),
                showgrid=False,
                secondary_y=True
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Price chart error: {e}")
            traceback.print_exc()
            return json.dumps({'error': str(e)})
    
    def create_interactive_technical_chart(self, df: pd.DataFrame, ticker: str) -> str:
        """Create technical analysis chart with RSI and MACD (3 subplots)"""
        try:
            if df is None or df.empty:
                return json.dumps({'error': 'No data available'})
            
            plot_df = df.tail(180).copy()
            plot_df = plot_df.reset_index()
            
            if 'Date' not in plot_df.columns:
                if 'index' in plot_df.columns:
                    plot_df = plot_df.rename(columns={'index': 'Date'})
                else:
                    plot_df['Date'] = pd.date_range(end=pd.Timestamp.now(), periods=len(plot_df), freq='D')
            
            dates = plot_df['Date'].dt.strftime('%Y-%m-%d').tolist()
            prices = plot_df['Close'].astype(float).tolist()
            
            # Calculate RSI
            delta = plot_df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
            rs = gain / loss
            rsi = (100 - (100 / (1 + rs))).fillna(50).tolist()
            
            # Calculate MACD
            exp12 = plot_df['Close'].ewm(span=12, adjust=False).mean()
            exp26 = plot_df['Close'].ewm(span=26, adjust=False).mean()
            macd = (exp12 - exp26).fillna(0).tolist()
            signal = pd.Series(macd).ewm(span=9, adjust=False).mean().fillna(0).tolist()
            histogram = [macd[i] - signal[i] for i in range(len(macd))]
            hist_colors = [self.colors['green'] if x >= 0 else self.colors['red'] for x in histogram]
            
            # Create subplot with 3 rows
            fig = make_subplots(
                rows=3, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.4, 0.3, 0.3],
                subplot_titles=(f'{ticker} - Price', 'RSI (14)', 'MACD')
            )
            
            # Price subplot
            fig.add_trace(
                go.Scatter(
                    x=dates, y=prices, mode='lines', name='Price',
                    line=dict(color=self.colors['blue'], width=2),
                    fill='tozeroy',
                    fillcolor='rgba(45, 127, 249, 0.1)',
                    hovertemplate='<b>Price</b>: $%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # RSI subplot
            fig.add_trace(
                go.Scatter(
                    x=dates, y=rsi, mode='lines', name='RSI',
                    line=dict(color=self.colors['gold'], width=2),
                    hovertemplate='<b>RSI</b>: %{y:.1f}<extra></extra>'
                ),
                row=2, col=1
            )
            
            # RSI threshold lines
            fig.add_hline(y=70, line_dash="dash", line_color=self.colors['red'], 
                         annotation_text="Overbought", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color=self.colors['green'], 
                         annotation_text="Oversold", row=2, col=1)
            
            # MACD subplot
            fig.add_trace(
                go.Scatter(
                    x=dates, y=macd, mode='lines', name='MACD',
                    line=dict(color=self.colors['blue'], width=1.5),
                    hovertemplate='<b>MACD</b>: %{y:.4f}<extra></extra>'
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=dates, y=signal, mode='lines', name='Signal',
                    line=dict(color=self.colors['orange'], width=1.5, dash='dash'),
                    hovertemplate='<b>Signal</b>: %{y:.4f}<extra></extra>'
                ),
                row=3, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=dates, y=histogram, name='Histogram',
                    marker=dict(color=hist_colors, opacity=0.7),
                    hovertemplate='<b>Histogram</b>: %{y:.4f}<extra></extra>'
                ),
                row=3, col=1
            )
            
            # Update layout
            fig.update_layout(
                title=dict(
                    text=f'{ticker} - Technical Analysis',
                    font=dict(size=16, color=self.colors['white'], family='Playfair Display'),
                    x=0.05
                ),
                height=650,
                hovermode='x unified',
                showlegend=True,
                plot_bgcolor='#161B22',
                paper_bgcolor='#161B22',
                font=dict(color=self.colors['white']),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color=self.colors['white'], size=9),
                    bgcolor='rgba(22, 27, 34, 0.8)',
                    bordercolor=self.colors['gold'],
                    borderwidth=1
                )
            )
            
            # Update axes
            fig.update_yaxes(
                title_text="Price (USD)",
                tickprefix='$',
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                title_font=dict(color=self.colors['white']),
                row=1, col=1
            )
            
            fig.update_yaxes(
                title_text="RSI",
                range=[0, 100],
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                title_font=dict(color=self.colors['white']),
                row=2, col=1
            )
            
            fig.update_yaxes(
                title_text="MACD",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                title_font=dict(color=self.colors['white']),
                row=3, col=1
            )
            
            fig.update_xaxes(
                title_text="Date",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                tickangle=-45,
                row=3, col=1
            )
            
            # Add range slider to price subplot
            fig.update_xaxes(rangeslider=dict(visible=True, thickness=0.05), row=1, col=1)
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Tech chart error: {e}")
            traceback.print_exc()
            return json.dumps({'error': str(e)})

    def create_interactive_returns_chart(self, df: pd.DataFrame, ticker: str) -> str:
        """Create returns distribution chart following the same pattern as price chart"""
        try:
            if df is None or df.empty:
                return json.dumps({'error': 'No data available'})
            
            # Calculate returns from the data
            close_prices = df['Close'].copy()
            
            # Calculate daily returns (%)
            returns = []
            for i in range(1, len(close_prices)):
                if close_prices.iloc[i-1] != 0:
                    ret = ((close_prices.iloc[i] - close_prices.iloc[i-1]) / close_prices.iloc[i-1]) * 100
                    returns.append(ret)
            
            # Debug output
            print(f"Returns calculated: {len(returns)} values")
            if len(returns) > 0:
                print(f"Returns range: {min(returns):.2f}% to {max(returns):.2f}%")
                print(f"Returns mean: {sum(returns)/len(returns):.2f}%")
            
            if len(returns) == 0:
                return json.dumps({'error': 'Insufficient data for returns calculation'})
            
            # Create figure with two subplots side by side
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=(f'{ticker} - Returns Distribution', f'{ticker} - Returns Summary'),
                specs=[[{'type': 'xy'}, {'type': 'xy'}]]
            )
            
            # Add histogram (like price line but for returns)
            fig.add_trace(
                go.Histogram(
                    x=returns,
                    nbinsx=40,
                    name='Returns Distribution',
                    marker=dict(
                        color=self.colors['blue'],
                        opacity=0.7,
                        line=dict(color=self.colors['white'], width=0.5)
                    ),
                    hovertemplate='<b>Return</b>: %{x:.2f}%<br><b>Frequency</b>: %{y}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Add mean line (like a reference line)
            mean_return = sum(returns) / len(returns)
            fig.add_vline(
                x=mean_return,
                line_dash="dash",
                line_color=self.colors['gold'],
                line_width=2,
                annotation_text=f"Mean: {mean_return:.2f}%",
                annotation_position="top",
                row=1, col=1
            )
            
            # Add median line
            sorted_returns = sorted(returns)
            median_return = sorted_returns[len(sorted_returns)//2]
            fig.add_vline(
                x=median_return,
                line_dash="dot",
                line_color=self.colors['orange'],
                line_width=1.5,
                annotation_text=f"Median: {median_return:.2f}%",
                annotation_position="bottom",
                row=1, col=1
            )
            
            # Add zero line
            fig.add_vline(
                x=0,
                line_dash="solid",
                line_color=self.colors['white'],
                line_width=1,
                opacity=0.3,
                row=1, col=1
            )
            
            # Add box plot (like volume on secondary axis)
            fig.add_trace(
                go.Box(
                    y=returns,
                    name='Returns Summary',
                    boxmean='sd',
                    marker_color=self.colors['gold'],
                    line_color=self.colors['gold'],
                    fillcolor=self.colors['blue'],
                    opacity=0.8,
                    hovertemplate='<b>Value</b>: %{y:.2f}%<extra></extra>'
                ),
                row=1, col=2
            )
            
            # Add horizontal line at zero on box plot
            fig.add_hline(
                y=0,
                line_dash="solid",
                line_color=self.colors['white'],
                line_width=1,
                opacity=0.3,
                row=1, col=2
            )
            
            # Update layout (following the same style as price chart)
            fig.update_layout(
                title=dict(
                    text=f'{ticker} - Daily Returns Analysis',
                    font=dict(size=16, color=self.colors['white'], family='Playfair Display'),
                    x=0.05
                ),
                height=500,
                hovermode='x unified',
                plot_bgcolor='#161B22',
                paper_bgcolor='#161B22',
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color=self.colors['white'], size=10),
                    bgcolor='rgba(22, 27, 34, 0.8)',
                    bordercolor=self.colors['gold'],
                    borderwidth=1
                ),
                margin=dict(l=60, r=60, t=80, b=50),
                bargap=0.05
            )
            
            # Update x-axis for histogram (left subplot)
            fig.update_xaxes(
                title_text="Daily Return (%)",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white'], size=10),
                title_font=dict(color=self.colors['white']),
                zerolinecolor='#2D3748',
                zerolinewidth=1,
                row=1, col=1
            )
            
            # Update y-axis for histogram (left subplot)
            fig.update_yaxes(
                title_text="Frequency",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white'], size=10),
                title_font=dict(color=self.colors['white']),
                zerolinecolor='#2D3748',
                row=1, col=1
            )
            
            # Update y-axis for box plot (right subplot)
            fig.update_yaxes(
                title_text="Return (%)",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white'], size=10),
                title_font=dict(color=self.colors['white']),
                zerolinecolor='#2D3748',
                row=1, col=2
            )
            
            # Remove x-axis title from box plot (not needed)
            fig.update_xaxes(
                showticklabels=False,
                showline=False,
                showgrid=False,
                row=1, col=2
            )
            
            print("Returns chart created successfully!")
            return fig.to_json()
            
        except Exception as e:
            print(f"Returns chart error: {e}")
            import traceback
            traceback.print_exc()
            return json.dumps({'error': str(e)})

    def create_interactive_peer_chart(self, peers_df: pd.DataFrame) -> str:
        """Create peer comparison chart"""
        try:
            if peers_df.empty:
                return json.dumps({'error': 'No peer data available'})
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('P/E Ratio Comparison', 'YTD Performance Comparison'),
                specs=[[{'type': 'bar'}, {'type': 'bar'}]]
            )
            
            # P/E Ratio
            fig.add_trace(
                go.Bar(
                    x=peers_df['company'],
                    y=peers_df['pe_ntm'],
                    name='P/E Ratio',
                    marker=dict(color=self.colors['blue'], opacity=0.8),
                    text=peers_df['pe_ntm'].apply(lambda x: f'{x:.1f}x' if isinstance(x, (int, float)) else 'N/A'),
                    textposition='outside',
                    textfont=dict(color=self.colors['white']),
                    hovertemplate='<b>%{x}</b><br>P/E Ratio: %{y:.1f}x<extra></extra>'
                ),
                row=1, col=1
            )
            
            # YTD Performance
            colors = [self.colors['green'] if x >= 0 else self.colors['red'] for x in peers_df['ytd_perf']]
            fig.add_trace(
                go.Bar(
                    x=peers_df['company'],
                    y=peers_df['ytd_perf'],
                    name='YTD Performance',
                    marker=dict(color=colors, opacity=0.8),
                    text=peers_df['ytd_perf'].apply(lambda x: f'{x:+.1f}%'),
                    textposition='outside',
                    textfont=dict(color=self.colors['white']),
                    hovertemplate='<b>%{x}</b><br>YTD: %{y:+.1f}%<extra></extra>'
                ),
                row=1, col=2
            )
            
            fig.add_hline(y=0, line_dash="dash", line_color=self.colors['gold'], row=1, col=2)
            
            fig.update_layout(
                title=dict(
                    text='Peer Comparison Analysis',
                    font=dict(size=16, color=self.colors['white'], family='Playfair Display'),
                    x=0.05
                ),
                height=450,
                plot_bgcolor='#161B22',
                paper_bgcolor='#161B22',
                font=dict(color=self.colors['white']),
                showlegend=False
            )
            
            fig.update_xaxes(
                tickangle=45,
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white'])
            )
            fig.update_yaxes(
                title_text="P/E Ratio (x)",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                row=1, col=1
            )
            fig.update_yaxes(
                title_text="YTD Performance (%)",
                gridcolor='#2D3748',
                tickfont=dict(color=self.colors['white']),
                row=1, col=2
            )
            
            return fig.to_json()
            
        except Exception as e:
            return json.dumps({'error': str(e)})