# Testing Guide

This guide helps you test the AI Review Intelligence System.

## Quick Test with Docker

1. **Start the system**:
   ```bash
   ./start.sh
   # Or manually: docker-compose up -d
   ```

2. **Wait for services to start** (30-60 seconds):
   ```bash
   docker-compose logs -f
   # Press Ctrl+C to stop following logs
   ```

3. **Run health check**:
   ```bash
   ./health-check.sh
   ```

4. **Access the application**:
   - Open browser to http://localhost:3000
   - You should see the dashboard

## Manual Testing Steps

### Test 1: Create Analysis Job

1. In the dashboard, fill in the form:
   - App Name: "Test App"
   - App ID: "com.test.app"
2. Click "Start Analysis"
3. The job should appear in the jobs list with status "queued"

### Test 2: Monitor Job Progress

1. Select the newly created job from the list
2. Watch as it progresses through states:
   - queued → fetching → analyzing → clustering → done
3. This should take 10-30 seconds

### Test 3: View Results

Once the job is complete:
1. Check the **Overview Stats**:
   - Total Reviews count
   - Average Rating
   - Sentiment distribution (Positive/Negative/Neutral)

2. Check **Themes & Tasks**:
   - Multiple themes should be identified
   - Each theme has associated tasks
   - RICE scores are calculated

3. Check **Sample Reviews**:
   - Individual reviews with ratings
   - Sentiment labels
   - Category tags (Bug, Feature, Usability, Praise)

### Test 4: RICE Prioritization

1. Find a task in the results
2. Click the Edit icon (pencil)
3. Modify RICE values:
   - Reach: 100
   - Impact: 5
   - Confidence: 90
   - Effort: 3
4. Click "Save"
5. Verify the RICE score updates

### Test 5: Task Confirmation

1. Find a task with pending status
2. Click the checkmark (✓) to confirm
3. Verify the task shows "✓ Confirmed"
4. Click the X to reject another task
5. Verify it shows "✗ Rejected"

## API Testing

### Using cURL

1. **Health check**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **Create job**:
   ```bash
   curl -X POST http://localhost:8000/api/jobs \
     -H "Content-Type: application/json" \
     -d '{"app_name": "Test App", "app_id": "com.test.app"}'
   ```

3. **List jobs**:
   ```bash
   curl http://localhost:8000/api/jobs
   ```

4. **Get job results** (replace {id}):
   ```bash
   curl http://localhost:8000/api/jobs/{id}/results
   ```

### Using Swagger UI

Visit http://localhost:8000/docs for interactive API documentation.

## Demo Mode

The system runs in demo mode by default (SERPAPI_KEY=demo_key), which generates mock reviews. This allows testing without a real SerpAPI key.

Mock reviews include:
- Various ratings (1-5 stars)
- Different sentiment levels
- Multiple categories (bugs, features, usability, praise)
- Realistic review content

## Troubleshooting

### Services not starting

```bash
# Check logs
docker-compose logs

# Restart services
docker-compose down
docker-compose up -d
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend not loading

```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### Celery worker not processing jobs

```bash
# Check Celery logs
docker-compose logs celery_worker

# Restart Celery
docker-compose restart celery_worker
```

## Performance Testing

For performance testing, you can create multiple jobs:

```bash
# Create 5 jobs
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/jobs \
    -H "Content-Type: application/json" \
    -d "{\"app_name\": \"Test App $i\", \"app_id\": \"com.test.app$i\"}"
done
```

## Expected Results

A successful test should show:
- ✓ All services running (postgres, redis, backend, celery_worker, frontend)
- ✓ Jobs progress through all states
- ✓ Reviews are analyzed and categorized
- ✓ Themes are identified
- ✓ Tasks are generated with RICE scores
- ✓ UI updates in real-time

## Cleaning Up

```bash
# Stop all services
docker-compose down

# Remove volumes (deletes data)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```
