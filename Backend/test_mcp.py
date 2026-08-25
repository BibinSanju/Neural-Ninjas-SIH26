import asyncio
from orchestrator.graph import mcp_client, create_agent_executor

async def main():
    await mcp_client.connect()
    res = await mcp_client.call_tool('search_knowledge_base', {'query': 'Alpha', 'clearance_level': '5'})
    print('RESULT:', res)
    await mcp_client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
