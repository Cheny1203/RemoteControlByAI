import asyncio
import os
from anthropic import Anthropic
from dotenv import load_dotenv
import speech_recognition as sr

load_dotenv()

class MapNavigationClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("请设置 ANTHROPIC_API_KEY 环境变量")
        
        self.client = Anthropic(api_key=api_key)
        self.recognizer = sr.Recognizer()
        
    def get_voice_input(self) -> str:
        print("\n请说话...")
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5)
                text = self.recognizer.recognize_google(audio, language='zh-CN')
                print(f"识别到: {text}")
                return text
            except sr.WaitTimeoutError:
                print("没有检测到语音输入")
                return ""
            except sr.UnknownValueError:
                print("无法识别语音")
                return ""
            except sr.RequestError as e:
                print(f"语音识别服务错误: {e}")
                return ""
    
    def get_text_input(self) -> str:
        return input("\n请输入导航指令 (例如: 从北京到上海): ")
    
    async def process_navigation_request(self, user_input: str, map_type: str = "baidu"):
        print(f"\n处理请求: {user_input}")
        print(f"使用地图: {map_type}")
        
        map_tool = "navigate_baidu_map" if map_type == "baidu" else "navigate_gaode_map"
        
        system_prompt = f"""你是一个导航助手。用户会告诉你起点和终点，你需要调用MCP工具来设置导航。
        
可用的MCP工具:
1. open_browser - 打开浏览器
2. {map_tool} - 在{'百度' if map_type == 'baidu' else '高德'}地图中设置导航，需要参数: start_location 和 end_location
3. close_browser - 关闭浏览器

请按照以下步骤操作:
1. 首先调用 open_browser 打开浏览器
2. 然后从用户输入中提取起点和终点，调用 {map_tool} 设置导航
3. 操作完成后给用户反馈

注意: 直接从用户的输入中提取地点名称，不要过度解析或改变地点名称。"""

        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        print("\n开始与AI交互...")
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=messages,
            tools=[
                {
                    "name": "open_browser",
                    "description": "打开浏览器并准备导航",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": map_tool,
                    "description": f"在{'百度' if map_type == 'baidu' else '高德'}地图中设置从起点到终点的导航路线",
                    "input_schema": {
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
                },
                {
                    "name": "close_browser",
                    "description": "关闭浏览器",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ],
            system=system_prompt
        )
        
        print(f"\nAI响应: {response.content}")
        
        if response.stop_reason == "tool_use":
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n执行工具: {block.name}")
                    print(f"参数: {block.input}")
                    
                    if block.name == "open_browser":
                        await self.simulate_open_browser()
                    elif block.name in ["navigate_baidu_map", "navigate_gaode_map"]:
                        await self.simulate_navigate(
                            block.input["start_location"],
                            block.input["end_location"],
                            map_type
                        )
        
        for block in response.content:
            if hasattr(block, "text"):
                print(f"\nAI说: {block.text}")
    
    async def simulate_open_browser(self):
        print("→ 模拟: 打开浏览器")
        from playwright.async_api import async_playwright
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        page = await browser.new_page()
        
        self.browser = browser
        self.playwright = playwright
        self.page = page
        
        print("✓ 浏览器已打开")
    
    async def simulate_navigate(self, start: str, end: str, map_type: str):
        import urllib.parse
        
        print(f"→ 模拟: 设置 {map_type} 地图导航 {start} → {end}")
        
        if not hasattr(self, 'page') or not self.page:
            print("错误: 浏览器未打开")
            return
        
        start_encoded = urllib.parse.quote(start)
        end_encoded = urllib.parse.quote(end)
        
        if map_type == "baidu":
            url = f"https://map.baidu.com/dir/{start_encoded}/{end_encoded}/@13520000,3570000,12z?querytype=nav&c=340&sn=2$$$$$$${start_encoded}$$$$$$&en=2$$$$$$${end_encoded}$$$$$$&sq={start_encoded}&eq={end_encoded}&mode=driving&route_traffic=1"
        else:
            url = f"https://www.amap.com/dir?from%5Bname%5D={start_encoded}&to%5Bname%5D={end_encoded}&type=car&policy=1"
        
        await self.page.goto(url)
        await self.page.wait_for_timeout(3000)
        
        print(f"✓ 已在{map_type}地图中设置导航")
    
    async def run(self):
        print("=" * 60)
        print("AI 地图导航助手")
        print("=" * 60)
        print("\n功能: 通过语音或文字控制浏览器打开地图并设置导航")
        print("支持: 百度地图、高德地图")
        print("\n命令:")
        print("  - 输入 'voice' 使用语音输入")
        print("  - 直接输入文字进行导航")
        print("  - 输入 'quit' 退出程序")
        
        while True:
            print("\n" + "-" * 60)
            choice = input("\n请选择输入方式 [text/voice/quit]: ").strip().lower()
            
            if choice == "quit":
                print("\n再见!")
                if hasattr(self, 'browser') and self.browser:
                    await self.browser.close()
                    await self.playwright.stop()
                break
            
            user_input = ""
            if choice == "voice":
                user_input = self.get_voice_input()
            else:
                user_input = self.get_text_input()
            
            if not user_input:
                continue
            
            map_choice = input("选择地图 [baidu/gaode, 默认百度]: ").strip().lower()
            map_type = "gaode" if map_choice == "gaode" else "baidu"
            
            await self.process_navigation_request(user_input, map_type)

async def main():
    try:
        client = MapNavigationClient()
        await client.run()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())
