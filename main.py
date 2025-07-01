import uuid
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from chat_engine import get_chain_for_session

app = FastAPI()

# allow your frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your Angular URL
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.post("/api/chat")
async def chat_endpoint(
    req: Request,
    response: Response,
    question: dict,
    session_id: str | None = Cookie(None)
):
    # 1) ensure session cookie
    if not session_id:
        session_id = str(uuid.uuid4())
        response.set_cookie("session_id", session_id, httponly=True)

    # 2) get chain for this session
    chain = get_chain_for_session(session_id)

    # 3) run the chain
    result = await chain.acall({"question": question["question"]})

    return JSONResponse({"answer": result["answer"]})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
