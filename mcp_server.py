import asyncio
import json
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from playwright.async_api import async_playwright, Browser, Page
import urllib.parse

class MapNavigationServer:
    def __init__(self):
        self.app = Server("map-navigation-server")
        self.browser: Browser | None = None
        self.page: Page | None = None
        self.playwright = None
        
        @self.app.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [
                Tool(
                    name="open_browser",
                    description="打开浏览器并准备导航",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="navigate_baidu_map",
                    description="在百度地图中设置从起点到终点的导航路线",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_location": {
                                "type": "string",
                                "description": "起点位置"
                            },
                            "end_location": {
                                "type": "string",
                                "description": "终点位置"
                            }
                        },
                        "required": ["start_location", "end_location"]
                    }
                ),
                Tool(
                    name="navigate_gaode_map",
                    description="在高德地图中设置从起点到终点的导航路线",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "start_location": {
                                "type": "string",
                                "description": "起点位置"
                            },
                            "end_location": {
                                "type": "string",
                                "description": "终点位置"
                            }
                        },
                        "required": ["start_location", "end_location"]
                    }
                ),
                Tool(
                    name="close_browser",
                    description="关闭浏览器",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.app.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            if name == "open_browser":
                return await self.open_browser()
            elif name == "navigate_baidu_map":
                return await self.navigate_baidu_map(
                    arguments["start_location"],
                    arguments["end_location"]
                )
            elif name == "navigate_gaode_map":
                return await self.navigate_gaode_map(
                    arguments["start_location"],
                    arguments["end_location"]
                )
            elif name == "close_browser":
                return await self.close_browser()
            else:
                return [TextContent(type="text", text=f"未知工具: {name}")]
    
    async def open_browser(self) -> list[TextContent]:
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False)
            self.page = await self.browser.new_page()
            return [TextContent(type="text", text="浏览器已成功打开")]
        except Exception as e:
            return [TextContent(type="text", text=f"打开浏览器失败: {str(e)}")]
    
    async def navigate_baidu_map(self, start: str, end: str) -> list[TextContent]:
        try:
            if not self.page:
                return [TextContent(type="text", text="请先打开浏览器")]

            start_encoded = urllib.parse.quote(start)
            end_encoded = urllib.parse.quote(end)

            # 使用步行模式 (mode=walking)
            # sn=2 和 en=2 表示自动选择最近的地点，不需要二次点击
            baidu_dir_url = f"https://map.baidu.com/dir/{start_encoded}/{end_encoded}/@13520000,3570000,12z?querytype=nav&c=340&sn=2$$$$$$${start_encoded}$$$$$$&en=2$$$$$$${end_encoded}$$$$$$&sq={start_encoded}&eq={end_encoded}&mode=walking&route_traffic=1"

            await self.page.goto(baidu_dir_url)
            await self.page.wait_for_timeout(3000)

            # 自动点击开始导航按钮（如果存在）
            try:
                # 等待页面加载完成
                await self.page.wait_for_timeout(2000)

                # 尝试点击"开始导航"或类似按钮
                # 百度地图的导航按钮可能有多种选择器
                start_nav_selectors = [
                    'text=开始导航',
                    'text=导航',
                    '[class*="start-nav"]',
                    '[class*="start-guide"]'
                ]

                for selector in start_nav_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=2000)
                        if element:
                            await element.click()
                            break
                    except:
                        continue

            except Exception as e:
                # 如果自动点击失败，只是记录，不影响主流程
                pass

            return [TextContent(type="text", text=f"已在百度地图中设置步行导航: {start} → {end}")]
        except Exception as e:
            return [TextContent(type="text", text=f"百度地图导航失败: {str(e)}")]
    
    async def navigate_gaode_map(self, start: str, end: str) -> list[TextContent]:
        try:
            if not self.page:
                return [TextContent(type="text", text="请先打开浏览器")]

            start_encoded = urllib.parse.quote(start)
            end_encoded = urllib.parse.quote(end)

            # 使用步行模式 (type=walk)
            # policy=1 表示推荐路线
            url = f"https://www.amap.com/dir?from%5Bname%5D={start_encoded}&to%5Bname%5D={end_encoded}&type=walk&policy=1"

            await self.page.goto(url)
            await self.page.wait_for_timeout(3000)

            # 自动点击开始导航按钮（如果存在）
            try:
                # 等待页面加载完成
                await self.page.wait_for_timeout(2000)

                # 尝试点击"开始导航"或类似按钮
                start_nav_selectors = [
                    'text=开始导航',
                    'text=导航',
                    '[class*="start-navi"]',
                    '[class*="route-start"]'
                ]

                for selector in start_nav_selectors:
                    try:
                        element = await self.page.wait_for_selector(selector, timeout=2000)
                        if element:
                            await element.click()
                            break
                    except:
                        continue

            except Exception as e:
                # 如果自动点击失败，只是记录，不影响主流程
                pass

            return [TextContent(type="text", text=f"已在高德地图中设置步行导航: {start} → {end}")]
        except Exception as e:
            return [TextContent(type="text", text=f"高德地图导航失败: {str(e)}")]
    
    async def close_browser(self) -> list[TextContent]:
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            return [TextContent(type="text", text="浏览器已关闭")]
        except Exception as e:
            return [TextContent(type="text", text=f"关闭浏览器失败: {str(e)}")]
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="map-navigation-server",
                    server_version="1.0.0",
                    capabilities=self.app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

async def main():
    server = MapNavigationServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
