"""
浏览器指纹生成模块
用于生成随机但真实的浏览器指纹,减少风控检测
"""

import random
import secrets
from typing import Dict, List, Tuple


class BrowserFingerprint:
    """浏览器指纹生成器"""
    
    # Chrome 版本列表 (最新的几个版本)
    CHROME_VERSIONS = [
        "120.0.6099.109",
        "121.0.6167.85",
        "122.0.6261.94",
        "123.0.6312.58",
        "124.0.6367.60",
    ]
    
    # 操作系统列表
    OS_LIST = [
        ("Windows NT 10.0; Win64; x64", "Windows"),
        ("Windows NT 11.0; Win64; x64", "Windows"),
        ("Macintosh; Intel Mac OS X 10_15_7", "macOS"),
        ("Macintosh; Intel Mac OS X 13_5_1", "macOS"),
        ("X11; Linux x86_64", "Linux"),
    ]
    
    # 屏幕分辨率
    SCREEN_RESOLUTIONS = [
        (1920, 1080),
        (2560, 1440),
        (1366, 768),
        (1536, 864),
        (1440, 900),
    ]
    
    # 语言列表
    LANGUAGES = [
        "en-US,en;q=0.9",
        "en-GB,en;q=0.9",
        "zh-CN,zh;q=0.9,en;q=0.8",
        "en-US,en;q=0.9,zh-CN;q=0.8",
    ]
    
    # 时区列表
    TIMEZONES = [
        "America/New_York",
        "America/Los_Angeles",
        "Europe/London",
        "Asia/Shanghai",
        "Asia/Tokyo",
    ]
    
    def __init__(self, seed: str = None):
        """
        初始化指纹生成器
        
        Args:
            seed: 随机种子,相同种子生成相同指纹
        """
        if seed:
            random.seed(seed)
        
        self.chrome_version = random.choice(self.CHROME_VERSIONS)
        self.os_string, self.os_name = random.choice(self.OS_LIST)
        self.screen_width, self.screen_height = random.choice(self.SCREEN_RESOLUTIONS)
        self.language = random.choice(self.LANGUAGES)
        self.timezone = random.choice(self.TIMEZONES)
        
        # 生成 WebGL 指纹
        self.webgl_vendor = self._generate_webgl_vendor()
        self.webgl_renderer = self._generate_webgl_renderer()
        
        # 生成 Canvas 指纹噪声
        self.canvas_noise = secrets.token_hex(16)
        
        # 生成硬件并发数 (CPU 核心数)
        self.hardware_concurrency = random.choice([4, 6, 8, 12, 16])
        
        # 生成设备内存 (GB)
        self.device_memory = random.choice([4, 8, 16, 32])
        
    def _generate_webgl_vendor(self) -> str:
        """生成 WebGL 供应商"""
        vendors = [
            "Google Inc. (NVIDIA)",
            "Google Inc. (Intel)",
            "Google Inc. (AMD)",
            "Google Inc. (Apple)",
        ]
        return random.choice(vendors)
    
    def _generate_webgl_renderer(self) -> str:
        """生成 WebGL 渲染器"""
        if "NVIDIA" in self.webgl_vendor:
            renderers = [
                "ANGLE (NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (NVIDIA GeForce GTX 1660 Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0)",
            ]
        elif "Intel" in self.webgl_vendor:
            renderers = [
                "ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0)",
            ]
        elif "AMD" in self.webgl_vendor:
            renderers = [
                "ANGLE (AMD Radeon RX 6700 XT Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (AMD Radeon RX 5700 Direct3D11 vs_5_0 ps_5_0)",
            ]
        else:
            renderers = [
                "ANGLE (Apple M1 Direct3D11 vs_5_0 ps_5_0)",
                "ANGLE (Apple M2 Direct3D11 vs_5_0 ps_5_0)",
            ]
        return random.choice(renderers)
    
    def get_user_agent(self) -> str:
        """生成 User-Agent"""
        webkit_version = f"537.{random.randint(30, 40)}"
        return (
            f"Mozilla/5.0 ({self.os_string}) "
            f"AppleWebKit/{webkit_version} (KHTML, like Gecko) "
            f"Chrome/{self.chrome_version} Safari/{webkit_version}"
        )
    
    def get_headers(self) -> Dict[str, str]:
        """生成完整的 HTTP 请求头"""
        headers = {
            "User-Agent": self.get_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": self.language,
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": str(random.choice([0, 1])),
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        # 随机添加一些可选头
        if random.random() > 0.5:
            headers["sec-ch-ua"] = self._generate_sec_ch_ua()
            headers["sec-ch-ua-mobile"] = "?0"
            headers["sec-ch-ua-platform"] = f'"{self.os_name}"'
        
        return headers
    
    def _generate_sec_ch_ua(self) -> str:
        """生成 sec-ch-ua 头"""
        major_version = self.chrome_version.split('.')[0]
        return (
            f'"Chromium";v="{major_version}", '
            f'"Google Chrome";v="{major_version}", '
            f'"Not=A?Brand";v="99"'
        )
    
    def get_fingerprint_data(self) -> Dict:
        """获取完整的指纹数据"""
        return {
            "userAgent": self.get_user_agent(),
            "language": self.language.split(',')[0],
            "languages": [lang.split(';')[0] for lang in self.language.split(',')],
            "platform": self.os_name,
            "screenResolution": f"{self.screen_width}x{self.screen_height}",
            "availableScreenResolution": f"{self.screen_width}x{self.screen_height - 40}",
            "colorDepth": 24,
            "pixelRatio": random.choice([1, 1.25, 1.5, 2]),
            "hardwareConcurrency": self.hardware_concurrency,
            "deviceMemory": self.device_memory,
            "timezone": self.timezone,
            "timezoneOffset": self._get_timezone_offset(),
            "webglVendor": self.webgl_vendor,
            "webglRenderer": self.webgl_renderer,
            "canvasNoise": self.canvas_noise,
            "audioNoise": secrets.token_hex(8),
            "fonts": self._generate_fonts_list(),
            "plugins": self._generate_plugins_list(),
            "doNotTrack": random.choice(["1", "unspecified"]),
            "cookieEnabled": True,
            "localStorage": True,
            "sessionStorage": True,
            "indexedDB": True,
        }
    
    def _get_timezone_offset(self) -> int:
        """获取时区偏移"""
        timezone_offsets = {
            "America/New_York": 300,
            "America/Los_Angeles": 480,
            "Europe/London": 0,
            "Asia/Shanghai": -480,
            "Asia/Tokyo": -540,
        }
        return timezone_offsets.get(self.timezone, 0)
    
    def _generate_fonts_list(self) -> List[str]:
        """生成字体列表"""
        common_fonts = [
            "Arial", "Verdana", "Helvetica", "Times New Roman", "Courier New",
            "Georgia", "Palatino", "Garamond", "Bookman", "Comic Sans MS",
            "Trebuchet MS", "Impact", "Lucida Console", "Tahoma", "Calibri",
        ]
        # 随机选择 10-15 个字体
        num_fonts = random.randint(10, 15)
        return random.sample(common_fonts, num_fonts)
    
    def _generate_plugins_list(self) -> List[Dict[str, str]]:
        """生成插件列表"""
        plugins = [
            {
                "name": "PDF Viewer",
                "description": "Portable Document Format",
                "filename": "internal-pdf-viewer",
            },
            {
                "name": "Chrome PDF Viewer",
                "description": "Portable Document Format",
                "filename": "internal-pdf-viewer",
            },
            {
                "name": "Chromium PDF Viewer",
                "description": "Portable Document Format",
                "filename": "internal-pdf-viewer",
            },
        ]
        return plugins


class FingerprintManager:
    """指纹管理器,为每个邮箱生成唯一指纹"""
    
    def __init__(self):
        self._fingerprints: Dict[str, BrowserFingerprint] = {}
    
    def get_fingerprint(self, email: str) -> BrowserFingerprint:
        """
        获取或创建指定邮箱的指纹
        
        Args:
            email: 邮箱地址
            
        Returns:
            BrowserFingerprint 对象
        """
        if email not in self._fingerprints:
            # 使用邮箱作为种子,确保同一邮箱总是使用相同指纹
            self._fingerprints[email] = BrowserFingerprint(seed=email)
        return self._fingerprints[email]
    
    def clear_fingerprint(self, email: str):
        """清除指定邮箱的指纹"""
        if email in self._fingerprints:
            del self._fingerprints[email]
    
    def clear_all(self):
        """清除所有指纹"""
        self._fingerprints.clear()


# 全局指纹管理器实例
_global_manager = FingerprintManager()


def get_fingerprint_for_email(email: str) -> BrowserFingerprint:
    """
    获取指定邮箱的浏览器指纹
    
    Args:
        email: 邮箱地址
        
    Returns:
        BrowserFingerprint 对象
    """
    return _global_manager.get_fingerprint(email)


def generate_random_fingerprint() -> BrowserFingerprint:
    """
    生成随机浏览器指纹
    
    Returns:
        BrowserFingerprint 对象
    """
    return BrowserFingerprint()


if __name__ == "__main__":
    # 测试代码
    print("=== 测试浏览器指纹生成 ===\n")
    
    # 生成随机指纹
    fp1 = generate_random_fingerprint()
    print("User-Agent:", fp1.get_user_agent())
    print("\n完整请求头:")
    for key, value in fp1.get_headers().items():
        print(f"  {key}: {value}")
    
    print("\n完整指纹数据:")
    import json
    print(json.dumps(fp1.get_fingerprint_data(), indent=2, ensure_ascii=False))
    
    # 测试相同邮箱生成相同指纹
    print("\n=== 测试指纹一致性 ===")
    email = "test@example.com"
    fp2 = get_fingerprint_for_email(email)
    fp3 = get_fingerprint_for_email(email)
    print(f"相同邮箱两次生成的 User-Agent 是否一致: {fp2.get_user_agent() == fp3.get_user_agent()}")
