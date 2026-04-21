# 1. Use a slim Python image as the base
FROM python:3.14-slim

# 2. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy only the dependency files first (for faster builds)
COPY pyproject.toml uv.lock ./

# 5. Install dependencies without the project itself
RUN uv sync --frozen --no-cache

# 6. Copy the rest of your code
COPY . .

# 7. Expose the port FastAPI runs on
EXPOSE 8000

# 8. Command to run the app
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
