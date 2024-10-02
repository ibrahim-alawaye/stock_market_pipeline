# Stock Market Data Pipeline

This project utilizes the Yahoo Finance API to retrieve Apple's stock data and process it using Astro CLI with Apache Airflow. The data is stored in MinIO, transformed, and then loaded into a PostgreSQL database for further analysis. Metabase is used for visualizing and analyzing the data through dashboards.

## API Overview

I used the following API URL to get Apple stock data directly from Yahoo Finance: https://query1.finance.yahoo.com/v8/finance/chart/aapl?metrics=high?&interval=1d&range=1y


## Project Workflow

1. **Fetch Data from Yahoo Finance API**:
    - The API fetches stock data for Apple Inc. (symbol: `AAPL`) using a daily interval for the past year.

2. **Astro CLI and Airflow**:
    - This project is set up using the Astro CLI, which simplifies the process of deploying and managing Apache Airflow.
    - The DAG is scheduled to run daily. It first checks the availability of the API using a sensor. 
    - If the API is available, it retrieves the stock prices using a Python operator.

3. **Store Raw Data**:
    - The raw stock data is saved into MinIO, which acts as the object storage system for this pipeline.

4. **Data Transformation**:
    - Using a Docker operator, the stock prices are transformed within a Spark container to clean and structure the data.

5. **Load Data into PostgreSQL**:
    - After the data is transformed, it is loaded into a PostgreSQL database, with a schema consisting of the following columns:
        - `timestamp`: Unix timestamp for the stock price.
        - `close`: Closing stock price.
        - `high`: Highest price for the day.
        - `low`: Lowest price for the day.
        - `open`: Opening price.
        - `volume`: Trading volume.
        - `date`: Date of the stock price.

6. **Analytics and Dashboarding with Metabase**:
    - Metabase is utilized to create visualizations and dashboards from the PostgreSQL database.
    - Users can interact with the dashboards to gain insights into Apple's stock performance over time.

## Installation

To set up the project, ensure you have the following prerequisites installed:

- Python 3.x
- Astro CLI
- Docker
- MinIO
- PostgreSQL
- Metabase

### Steps:

Clone the repository:
   ```bash
   git clone https://github.com/ibrahim-alawaye/stock_market_pipeline/.git
   cd stock_market_pipeline

## Environment Setup using Astro CLI and Metabase

### 1. Initialize Astro CLI

To initialize Astro CLI for local Airflow development, run the following command:

```bash
astro dev init
```

This will create the necessary configuration files for your Astro CLI environment.

### 2. Start the Astro CLI Local Environment

After initializing the environment, start the local Airflow instance with the following command:

```bash
astro dev start
```

This starts the Airflow services, including the web server, scheduler, and any other required components.

### 3. Access the Airflow UI

Once the environment is running, access the Airflow UI by navigating to:

```
http://localhost:8080
```

Here you can monitor and manually trigger your DAGs.

### 4. Access Metabase

Access Metabase by opening your browser and navigating to:

```
http://localhost:3000
```

Once there, follow the setup instructions to get Metabase ready.

### 6. Connect Metabase to PostgreSQL

In Metabase, connect to your PostgreSQL database to start building dashboards. You can create insightful visualizations based on the data processed through your Airflow pipelines.

### Usage

- **Airflow**: Use the Airflow UI to manually trigger DAGs and monitor their status. Review task logs for debugging and analyzing pipeline performance.
  
- **Metabase**: Explore your data and create dashboards with Metabase. Use the SQL editor for queries and customize your visualizations.

### License

This project is licensed under the MIT License.
```


