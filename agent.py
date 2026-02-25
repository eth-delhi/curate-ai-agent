
from uagents import Agent, Context

agent = Agent()


@agent.on_event("startup")
async def introduce_agent(ctx: Context):
    ctx.logger.info(f"Hello, I'm an agent and my address is {ctx.agent.address}.")


if __name__ == "__main__":
    agent.run()
