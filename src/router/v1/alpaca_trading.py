from fastapi import APIRouter


alpaca_trading = APIRouter(
    prefix="/alpaca",
    tags=["alpaca"],
    responses={404: {"description": "Not found"}}
)


@alpaca_trading.get("/")
async def v1resp():
    return {"message": "Alpaca trading"}


@alpaca_trading.get("/{num}")
async def v1resp(num: int):
    return {"message": f"num={num}"}
