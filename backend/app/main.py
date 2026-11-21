from fastapi import FastAPI
from fastapi.middleware.cors import  CORSMiddleware



app = FastAPI()


#Default behaviour of browser is to reject/not show response from other site which came due to req by our site, so this part of our code lets browser to allow response for a specific host set in allow_origins

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173"],
  allow_methods=["*"],
  allow_headers=["*"],
)

@app.get("/")
def home():
  return{"message": "hello from droppin"}


  