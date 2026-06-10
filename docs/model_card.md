# Model Card — NBA Player Prop Predictor

## Overview
Three XGBoost regression models predicting NBA player performance for prop betting:
- **Points model** — predicts total points scored
- **Rebounds model** — predicts total rebounds
- **Assists model** — predicts total assists

## Training Data
- **Source**: NBA Stats API via nba_api Python library
- **Players**: 50 active NBA players
- **Seasons**: 2023-24, 2024-25
- **Total rows**: ~4,800 player-game records
- **Train/test split**: 80/20 time-based (no shuffle to prevent leakage)

## Features (39 total)
- **Rolling averages**: 5/10/20-game windows for pts, reb, ast, min, tov
- **Lag features**: Last 1/2/3 game performance for pts, reb, ast, min
- **Efficiency metrics**: FG%, 3P%, FT%, true shooting %, assist/turnover ratio
- **Game context**: Home/away, days rest, back-to-back, game number, day of week
- **Opponent**: Opponent defensive ratings for pts/reb/ast allowed

## Model Architecture
- **Algorithm**: XGBoost Regressor
- **Tuning**: Optuna (30 trials, TimeSeriesSplit cross-validation)
- **Tracking**: MLflow experiment tracking

## Performance

| Metric | Points | Rebounds | Assists |
|---|---|---|---|
| MAE | 2.061 | 2.158 | 0.652 |
| Within 3 | 77.5% | 76.2% | 96.3% |
| Within 5 | 90.9% | 92.3% | 99.3% |
| Within 10 | 98.6% | 99.4% | 100%|
| Bet accuracy | 91.5% | 76.4% | 85% |

*(Update TBD values with backtest results)*

## Limitations
- Trained on 50 players only — may underperform for players not in training set
- Does not account for injuries, lineup changes, or trade deadline moves
- Opponent defensive ratings are season averages — does not capture recent defensive form
- Model retrains on historical data only — real-time updates require pipeline rerun
- Prop lines from sportsbooks incorporate information this model does not have access to

## Intended Use
- Educational and research purposes
- Demonstrating end-to-end ML system design
- Not intended for actual financial betting decisions

## Author
[@krsngth22](https://github.com/krsngth22)
