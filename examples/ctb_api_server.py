#!/usr/bin/env python3
"""
CTB系统API服务器

提供CTB系统的预测和技能应用功能
"""

import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 确保项目根目录在sys.path中
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from game_system.ctb.ctb_system import CTBManager, Character
from game_system.game_time.time_system import TimeManager
from examples.data.ctb_characters import create_sample_characters

# 全局CTB管理器实例
ctb_manager = None

class CTBAPIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if path == '/api/predict':
            self.handle_predict(query_params)
        elif path == '/api/apply_skill':
            self.handle_apply_skill(query_params)
        elif path == '/api/status':
            self.handle_status()
        else:
            self.send_error(404, "API endpoint not found")

    def do_POST(self):
        """处理POST请求"""
        parsed_url = urlparse(self.path)
        path = parsed_url.path

        if path == '/api/apply_skill':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            self.handle_apply_skill_post(data)
        else:
            self.send_error(404, "API endpoint not found")

    def handle_predict(self, params):
        """处理预测请求"""
        try:
            character_id = params.get('character_id', [None])[0]
            delay_hours = int(params.get('delay_hours', [0])[0])

            if character_id and delay_hours <= 0:
                self.send_error(400, "delay_hours must be positive")
                return

            predicted_actions = ctb_manager.predict_action_order(character_id, delay_hours)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'success': True,
                'predicted_actions': predicted_actions,
                'delay_applied': character_id is not None and delay_hours > 0
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Prediction failed: {str(e)}")

    def handle_apply_skill(self, params):
        """处理技能应用请求（GET方式）"""
        try:
            character_id = params.get('character_id', [None])[0]
            delay_hours = int(params.get('delay_hours', [0])[0])

            if not character_id or delay_hours <= 0:
                self.send_error(400, "character_id and positive delay_hours required")
                return

            success = ctb_manager.apply_delay_skill(character_id, delay_hours)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'success': success,
                'message': f"Skill applied to {character_id} with {delay_hours} hours delay" if success else "Failed to apply skill"
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Skill application failed: {str(e)}")

    def handle_apply_skill_post(self, data):
        """处理技能应用请求（POST方式）"""
        try:
            character_id = data.get('character_id')
            delay_hours = data.get('delay_hours', 0)

            if not character_id or delay_hours <= 0:
                self.send_error(400, "character_id and positive delay_hours required")
                return

            success = ctb_manager.apply_delay_skill(character_id, delay_hours)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'success': success,
                'message': f"Skill applied to {character_id} with {delay_hours} hours delay" if success else "Failed to apply skill"
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Skill application failed: {str(e)}")

    def handle_status(self):
        """处理状态查询请求"""
        try:
            character_info = ctb_manager.get_character_info()
            next_action = ctb_manager.get_action_list(1)

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            response = {
                'success': True,
                'characters': character_info,
                'next_action': next_action[0] if next_action else None
            }

            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f"Status query failed: {str(e)}")

    def log_message(self, format, *args):
        """自定义日志格式"""
        print(f"[CTB API] {format % args}")

def initialize_ctb_system():
    """初始化CTB系统"""
    global ctb_manager

    # 创建时间管理器
    time_manager = TimeManager()

    # 创建CTB管理器
    ctb_manager = CTBManager(time_manager)

    # 添加示例角色
    characters = create_sample_characters()
    for character in characters:
        ctb_manager.add_character(character)

    # 初始化CTB系统
    ctb_manager.initialize_ctb()

    print("✅ CTB系统已初始化")

def main():
    """主函数"""
    print("🚀 启动CTB API服务器...")

    # 初始化CTB系统
    initialize_ctb_system()

    # 设置服务器
    port = 8001
    server = HTTPServer(('localhost', port), CTBAPIHandler)

    print(f"📍 CTB API服务器地址: http://localhost:{port}")
    print("📋 可用API端点:")
    print("  - GET /api/predict?character_id=xxx&delay_hours=5")
    print("  - POST /api/apply_skill (JSON body)")
    print("  - GET /api/status")
    print("\n🔄 服务器运行中... (按 Ctrl+C 退出)")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
        server.shutdown()

if __name__ == '__main__':
    main()