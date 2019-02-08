from fastapi import FastAPI

app = FastAPI(title="DECIDIM Pilot connector",
              description="Mission: connect DDDC to Chainspace",
              version="0.0.1",)


@app.get("/")
def root():
    return {"message": "Hello World"}
