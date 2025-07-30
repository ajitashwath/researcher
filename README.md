# Researcher Agent
## Features

- 🤖 **Multi-Agent AI System**: Research, analysis, writing, and review agents working together
- 📊 **Comprehensive Reports**: Generate detailed reports on any topic
- 🌐 **Multiple Interfaces**: Web UI (Streamlit), REST API (FastAPI), and CLI
- ☁️ **Cloud-Ready**: Docker containerization with GCP deployment support
- 🔧 **Configurable**: Customizable agents, tasks, and report formats
- 🔍 **Advanced Research**: Integration with search tools and OpenAI for comprehensive research

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

```bash
# Install using pip
pip install -r requirements.txt

# Or using crewai CLI (optional)
crewai install
```

## Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# Optional Configuration
PYTHONDONTWRITEBYTECODE=1
PYTHONUNBUFFERED=1
```

**Required API Keys:**
- `OPENAI_API_KEY`: For AI content generation and analysis
- `GROQ_API_KEY`: For enhanced AI processing capabilities
- `SERPER_API_KEY`: For web search functionality

## Usage Options

### 1. Streamlit Web Interface

Run the interactive web application:

```bash
streamlit run app.py
```

Access the application at `http://localhost:8501`

### 2. FastAPI REST API

Start the API server:

```bash
# Development
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn -w 1 --threads 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 api:app
```

**API Endpoints:**
- `GET /`: Health check
- `POST /research`: Generate reports

**Example API Usage:**
```bash
curl -X POST "http://localhost:8000/research" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "How to improve infrastructure in Bangalore?",
    "user_personalization": "Focus on transportation and urban planning"
  }'
```

### 3. Command Line Interface

Run directly from the command line:

```bash
crewai run
```

This will generate a `report.md` file with research on LLMs (default example).

## Docker Deployment

### Building the Docker Image

The project includes a production-ready Dockerfile optimized for deployment:

```bash
# Build the image
docker build -t createreport-crew .

# Run locally
docker run -p 8080:8080 \
  -e OPENAI_API_KEY=your_key_here \
  -e GROQ_API_KEY=your_key_here \
  -e SERPER_API_KEY=your_key_here \
  createreport-crew
```

### Docker Configuration

The Dockerfile is configured with:
- **Base Image**: Python 3.11 slim (Debian Bullseye)
- **Port**: 8080 (Cloud Run compatible)
- **Server**: Gunicorn with Uvicorn workers
- **Optimization**: Multi-threaded, production-ready configuration

## Google Cloud Platform (GCP) Deployment

### Prerequisites

1. Install Google Cloud SDK:
```bash
# macOS
brew install google-cloud-sdk

# Ubuntu/Debian
sudo apt-get install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

2. Authenticate with GCP:
```bash
gcloud auth login
```

### Step-by-Step GCP Deployment

#### 1. Project Setup

```bash
# List available projects
gcloud projects list

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required services
gcloud services enable cloudbuild.googleapis.com artifactregistry.googleapis.com run.googleapis.com
```

#### 2. Configure Variables

```powershell
# PowerShell (Windows)
$REPO_NAME = "createreport-crew"
$REGION = "us-central1"  # or your preferred region
$SERVICE_NAME = "createreport-api"
```

```bash
# Bash (Linux/macOS)
REPO_NAME="createreport-crew"
REGION="us-central1"  # or your preferred region
SERVICE_NAME="createreport-api"
```

#### 3. Create Artifact Registry Repository

```powershell
# PowerShell
gcloud artifacts repositories create $REPO_NAME `
    --repository-format=docker `
    --location=$REGION `
    --description="CreateReport Crew Docker Repository"
```

```bash
# Bash
gcloud artifacts repositories create $REPO_NAME \
    --repository-format=docker \
    --location=$REGION \
    --description="CreateReport Crew Docker Repository"
```

#### 4. Build and Push Docker Image

```powershell
# PowerShell
$PROJECT_ID = $(gcloud config get-value project)
$IMAGE_TAG = "$($REGION)-docker.pkg.dev/$($PROJECT_ID)/$($REPO_NAME)/createreport-api:latest"

# Build and push image
gcloud builds submit --tag $IMAGE_TAG
```

```bash
# Bash
PROJECT_ID=$(gcloud config get-value project)
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/createreport-api:latest"

# Build and push image
gcloud builds submit --tag $IMAGE_TAG
```

#### 5. Deploy to Cloud Run

```powershell
# PowerShell
gcloud run deploy $SERVICE_NAME `
    --image=$IMAGE_TAG `
    --platform=managed `
    --region=$REGION `
    --allow-unauthenticated `
    --port=8080 `
    --memory=2Gi `
    --cpu=1 `
    --timeout=900 `
    --set-env-vars="PYTHONDONTWRITEBYTECODE=1,PYTHONUNBUFFERED=1"
```

```bash
# Bash
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --platform=managed \
    --region=$REGION \
    --allow-unauthenticated \
    --port=8080 \
    --memory=2Gi \
    --cpu=1 \
    --timeout=900 \
    --set-env-vars="PYTHONDONTWRITEBYTECODE=1,PYTHONUNBUFFERED=1"
```

#### 6. Set Environment Variables (Secrets)

For production deployment, set your API keys as environment variables:

```bash
# Set environment variables with secrets
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --set-env-vars="OPENAI_API_KEY=your_openai_key_here,GROQ_API_KEY=your_groq_key_here,SERPER_API_KEY=your_serper_key_here"
```

**Better approach using Secret Manager:**

```bash
# Create secrets
echo "your_openai_key_here" | gcloud secrets create openai-api-key --data-file=-
echo "your_groq_key_here" | gcloud secrets create groq-api-key --data-file=-
echo "your_serper_key_here" | gcloud secrets create serper-api-key --data-file=-

# Deploy with secrets
gcloud run deploy $SERVICE_NAME \
    --image=$IMAGE_TAG \
    --region=$REGION \
    --set-secrets="OPENAI_API_KEY=openai-api-key:latest,GROQ_API_KEY=groq-api-key:latest,SERPER_API_KEY=serper-api-key:latest"
```

### Post-Deployment

After successful deployment, you'll receive a service URL. You can:

1. **Test the API**:
```bash
curl -X GET "https://your-service-url.run.app/"
```

2. **View logs**:
```bash
gcloud run services logs tail $SERVICE_NAME --region=$REGION
```

3. **Monitor the service**:
```bash
gcloud run services describe $SERVICE_NAME --region=$REGION
```

## Customization

### Agents Configuration

Modify `src/create_report/config/agents.yaml` to define your agents:

```yaml
researcher:
  role: "Senior Research Analyst" 
  goal: "Conduct comprehensive research..."
  backstory: "You are a senior research analyst..."
```

### Tasks Configuration

Modify `src/create_report/config/tasks.yaml` to define your tasks:

```yaml
research_task:
  description: "Conduct comprehensive research on..."
  expected_output: "A comprehensive research summary..."
  agent: researcher
```

### Custom Logic

- **Modify `src/create_report/crew.py`**: Add custom logic, tools, and specific arguments
- **Modify `src/create_report/main.py`**: Add custom inputs and orchestration logic
- **Modify `api.py`**: Customize API endpoints and request handling
- **Modify `app.py`**: Customize the Streamlit interface

## Project Structure

```
create_report/
├── .dockerignore           # Docker ignore patterns
├── .gitignore             # Git ignore patterns  
├── Dockerfile             # Production Docker configuration
├── README.md              # This file
├── api.py                 # FastAPI REST API
├── app.py                 # Streamlit web interface
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── knowledge/            # Knowledge base files
│   └── user_preference.txt
├── src/create_report/    # Main package
│   ├── __init__.py
│   ├── main.py           # Main orchestration logic
│   ├── crew.py           # Crew management
│   ├── config/           # Configuration files
│   │   ├── agents.yaml   # Agent definitions
│   │   └── tasks.yaml    # Task definitions
│   └── tools/            # Custom tools
│       ├── __init__.py
│       └── custom_tool.py
```

## Understanding Your Crew

The create-report Crew is composed of multiple AI agents, each with unique roles, goals, and tools:

- **🔍 Researcher**: Conducts comprehensive research and gathers information
- **📊 Analyst**: Analyzes data and identifies trends and insights  
- **✍️ Writer**: Creates well-structured, engaging reports
- **🔍 Reviewer**: Reviews and improves report quality and accuracy
- **📋 Strategist**: Develops strategic recommendations and implementation plans

These agents collaborate on a series of tasks, leveraging their collective skills to achieve complex objectives.

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in your environment
2. **Docker Build Failures**: Check that all dependencies are properly listed in `requirements.txt`
3. **GCP Deployment Issues**: Verify that all required GCP services are enabled
4. **Memory Issues**: Increase Cloud Run memory allocation if processing large reports

### Docker Debugging

```bash
# Build and run locally for debugging
docker build -t createreport-crew-debug .
docker run -it --entrypoint /bin/bash createreport-crew-debug

# Check logs
docker logs <container_id>
```

### GCP Debugging

```bash
# View detailed logs
gcloud run services logs tail $SERVICE_NAME --region=$REGION --format="value(textPayload)"

# Check service status
gcloud run services list --region=$REGION

# Describe service configuration
gcloud run services describe $SERVICE_NAME --region=$REGION
```

## Performance Optimization

For better performance in production:

1. **Increase Resources**: Adjust CPU and memory in Cloud Run deployment
2. **Enable Caching**: Implement caching for frequently requested reports
3. **Database Integration**: Add database support for storing reports and user data
4. **Load Balancing**: Use multiple Cloud Run instances for high traffic

## Support

For support, questions, or feedback regarding the CreateReport Crew or crewAI:

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)
