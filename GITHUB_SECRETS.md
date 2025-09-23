# GitHub Actions Secrets and Variables

This document lists the required secrets and variables for the GitHub Actions workflows in this repository.

## Secrets

### For the `deploy.yml` workflow:

*   `DIGITALOCEAN_ACCESS_TOKEN`: Your access token for the DigitalOcean API.
*   `DIGITALOCEAN_APP_ID`: The ID of your app in DigitalOcean.
*   `DISCORD_WEBHOOK`: The URL of the Discord webhook for sending notifications.
*   `VPS_HOST`: The IP address or hostname of your Virtual Private Server.
*   `VPS_USERNAME`: The username for SSH access to your VPS.
*   `VPS_SSH_KEY`: The private SSH key for authenticating with your VPS.
*   `VPS_PORT`: The SSH port of your VPS (usually 22).
*   `GEMINI_API_KEY`: Your API key for the Gemini cryptocurrency exchange.
*   `NEWSDATA_API_KEY`: Your API key for NewsData.io.
*   `ALPHAVANTAGE_API_KEY`: Your API key for Alpha Vantage.
*   `NEWSAPI_ORG_KEY`: Your API key for NewsAPI.org.
*   `FINNHUB_API_KEY`: Your API key for Finnhub.
*   `FMP_API_KEY`: Your API key for Financial Modeling Prep.
*   `REDDIT_CLIENT_ID`: The client ID for your Reddit API application.
*   `REDDIT_CLIENT_SECRET`: The client secret for your Reddit API application.
*   `REDDIT_USERNAME`: The Reddit username associated with your application.
*   `REDDIT_PASSWORD`: The Reddit password for the user.
*   `BYBIT_API_KEY`: Your API key for the Bybit exchange.
*   `BYBIT_API_SECRET`: Your API secret for the Bybit exchange.
*   `DISCORD_TOKEN`: The token for your Discord bot.
*   `TELEGRAM_TOKEN`: The token for your Telegram bot.

### For the `docker-image.yml` workflow:

*   `DOCKER_USERNAME`: Your Docker Hub username.
*   `DOCKER_PASSWORD`: Your Docker Hub password or access token.

## Variables

*   `APP_URL`: The URL where your application will be accessible after deployment on DigitalOcean. This is used in the `deploy.yml` workflow to verify the deployment.

## How to Add Secrets and Variables

1.  Go to your repository on GitHub.
2.  Click on the **Settings** tab.
3.  In the left sidebar, under the "Security" section, click on **Secrets and variables**, then **Actions**.
4.  To add a secret, click the **New repository secret** button. Enter the name of the secret (e.g., `DIGITALOCEAN_ACCESS_TOKEN`) and its value, then click **Add secret**.
5.  To add a variable, click the **Variables** tab, then the **New repository variable** button. Enter the name of the variable (e.g., `APP_URL`) and its value, then click **Add variable**.

Repeat these steps for all the secrets and variables listed above.
