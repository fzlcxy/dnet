"""
配置文件管理模块
"""
import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

from dnet_parser import DnetFile


@dataclass
class S2CResponse:
    """S2C响应配置"""
    protocol: str
    order: int
    type: str = "必然回包"  # "必然回包" 或 "按条件回包"
    condition: str = ""
    count: str = "一次"  # "一次" 或 "多次"
    order_group: str = ""  # 顺序组名称，相同组名表示顺序不确定，空表示确定顺序
    ordered: bool = True  # 是否有序，True=顺序(数字序号)，False=无序(x标记)
    cmodule: str = ""  # S2C协议所属dnet文件的CMODULE


@dataclass
class S2CTrigger:
    """S2C自定义触发条件"""
    name: str  # 触发条件名称/描述
    type: str = "必然回包"  # "必然回包" 或 "按条件回包"
    condition: str = ""  # 备注说明
    count: str = "一次"  # "一次" 或 "多次"
    ordered: bool = True  # 是否有序


@dataclass
class S2CTriggerConfig:
    """单个S2C的触发条件配置"""
    custom_triggers: List[S2CTrigger] = field(default_factory=list)


@dataclass
class OrderGroup:
    """顺序组定义"""
    name: str  # 组名，如 "A", "B"
    description: str = ""  # 组说明，如 "这两个包顺序不确定"


@dataclass
class C2SMapping:
    """单个C2S的映射配置"""
    description: str
    responses: List[S2CResponse] = field(default_factory=list)
    order_groups: List[OrderGroup] = field(default_factory=list)  # 顺序组定义


@dataclass
class C2SConfig:
    """整个.dnet文件的配置"""
    dnet_file: str
    description: str
    c2s_mappings: Dict[str, C2SMapping] = field(default_factory=dict)
    s2c_triggers: Dict[str, S2CTriggerConfig] = field(default_factory=dict)  # S2C自定义触发条件


class ConfigManager:
    """配置文件管理器"""

    def __init__(self, proto_root: str, config_root: str):
        self.proto_root = proto_root
        self.config_root = config_root

    def get_config_path(self, dnet_relative_path: str) -> str:
        """根据.dnet相对路径获取对应的JSON配置文件路径"""
        json_path = os.path.splitext(dnet_relative_path)[0] + '.json'
        return os.path.join(self.config_root, json_path)

    def load_config(self, dnet_relative_path: str) -> Optional[C2SConfig]:
        """加载配置文件"""
        config_path = self.get_config_path(dnet_relative_path)

        if not os.path.exists(config_path):
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._dict_to_config(data)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"加载配置文件失败: {config_path}, 错误: {e}")
            return None

    def save_config(self, dnet_relative_path: str, config: C2SConfig) -> bool:
        """保存配置到JSON文件"""
        config_path = self.get_config_path(dnet_relative_path)

        # 创建目录（如果不存在）
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

        try:
            data = self._config_to_dict(config)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {config_path}, 错误: {e}")
            return False

    def validate_config(self, config: C2SConfig, dnet: DnetFile,
                       all_dnet_files: List[DnetFile]) -> List[str]:
        """
        验证配置的有效性
        返回警告信息列表
        """
        warnings = []

        # 构建所有可用的S2C协议集合
        all_s2c_protocols = set()
        for df in all_dnet_files:
            for s2c in df.s2c_list:
                all_s2c_protocols.add(s2c.name)

        # 检查每个C2S的配置
        for c2s_name, mapping in config.c2s_mappings.items():
            # 检查C2S是否存在于dnet文件中
            c2s_exists = any(p.name == c2s_name for p in dnet.c2s_list)
            if not c2s_exists:
                warnings.append(f"C2S协议 '{c2s_name}' 不存在于 {dnet.file_name} 中")

            # 检查配置的S2C是否存在
            for resp in mapping.responses:
                if resp.protocol not in all_s2c_protocols:
                    warnings.append(
                        f"C2S '{c2s_name}' 配置的S2C '{resp.protocol}' 不存在于任何.dnet文件中"
                    )

        return warnings

    def create_empty_config(self, dnet: DnetFile) -> C2SConfig:
        """为.dnet文件创建空配置"""
        config = C2SConfig(
            dnet_file=dnet.file_name,
            description=dnet.description
        )

        # 为每个C2S创建空的映射
        for c2s in dnet.c2s_list:
            config.c2s_mappings[c2s.name] = C2SMapping(
                description=c2s.description
            )

        return config

    def _config_to_dict(self, config: C2SConfig) -> dict:
        """将配置对象转换为字典"""
        result = {
            "dnet_file": config.dnet_file,
            "description": config.description,
            "c2s_mappings": {
                c2s_name: {
                    "description": mapping.description,
                    "order_groups": [
                        {"name": g.name, "description": g.description}
                        for g in mapping.order_groups
                    ],
                    "responses": [
                        {
                            "protocol": r.protocol,
                            "order": r.order,
                            "type": r.type,
                            "condition": r.condition,
                            "count": r.count,
                            "order_group": r.order_group,
                            "ordered": r.ordered,
                            "cmodule": r.cmodule
                        }
                        for r in mapping.responses
                    ]
                }
                for c2s_name, mapping in config.c2s_mappings.items()
            }
        }
        # 添加S2C触发条件（如果有）
        if config.s2c_triggers:
            result["s2c_triggers"] = {
                s2c_name: {
                    "custom_triggers": [
                        {
                            "name": t.name,
                            "type": t.type,
                            "condition": t.condition,
                            "count": t.count,
                            "ordered": t.ordered
                        }
                        for t in trigger_config.custom_triggers
                    ]
                }
                for s2c_name, trigger_config in config.s2c_triggers.items()
                if trigger_config.custom_triggers  # 只保存有数据的
            }
        return result

    def _dict_to_config(self, data: dict) -> C2SConfig:
        """将字典转换为配置对象"""
        config = C2SConfig(
            dnet_file=data.get("dnet_file", ""),
            description=data.get("description", "")
        )

        for c2s_name, mapping_data in data.get("c2s_mappings", {}).items():
            responses = []
            for r in mapping_data.get("responses", []):
                # 兼容旧格式：order_group可能是int或str
                order_group = r.get("order_group", "")
                if isinstance(order_group, int):
                    order_group = chr(64 + order_group) if order_group > 0 else ""
                responses.append(S2CResponse(
                    protocol=r.get("protocol", ""),
                    order=r.get("order", 0),
                    type=r.get("type", "必然回包"),
                    condition=r.get("condition", ""),
                    count=r.get("count", "一次"),
                    order_group=order_group,
                    ordered=r.get("ordered", True),  # 兼容旧数据，默认为有序
                    cmodule=r.get("cmodule", "")
                ))
            order_groups = []
            for g in mapping_data.get("order_groups", []):
                order_groups.append(OrderGroup(
                    name=g.get("name", ""),
                    description=g.get("description", "")
                ))
            config.c2s_mappings[c2s_name] = C2SMapping(
                description=mapping_data.get("description", ""),
                responses=responses,
                order_groups=order_groups
            )

        # 加载S2C触发条件
        for s2c_name, trigger_data in data.get("s2c_triggers", {}).items():
            triggers = []
            for t in trigger_data.get("custom_triggers", []):
                triggers.append(S2CTrigger(
                    name=t.get("name", ""),
                    type=t.get("type", "必然回包"),
                    condition=t.get("condition", ""),
                    count=t.get("count", "一次"),
                    ordered=t.get("ordered", True)
                ))
            config.s2c_triggers[s2c_name] = S2CTriggerConfig(custom_triggers=triggers)

        return config

    def export_config(self, config: C2SConfig, export_path: str) -> bool:
        """导出配置到指定路径"""
        try:
            data = self._config_to_dict(config)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False

    def import_config(self, import_path: str) -> Optional[C2SConfig]:
        """从指定路径导入配置"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self._dict_to_config(data)
        except Exception as e:
            print(f"导入配置失败: {e}")
            return None


if __name__ == '__main__':
    # 测试代码
    from dnet_parser import DnetParser

    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    proto_dir = os.path.join(root_dir, 'proto')
    config_dir = os.path.join(root_dir, 'clientconfig')

    parser = DnetParser()
    manager = ConfigManager(proto_dir, config_dir)

    dnet_files = parser.scan_directory(proto_dir)

    if dnet_files:
        dnet = dnet_files[0]
        print(f"测试文件: {dnet.relative_path}")

        # 创建空配置
        config = manager.create_empty_config(dnet)
        print(f"创建空配置: {config.dnet_file}")

        # 添加一些测试数据
        if dnet.c2s_list:
            c2s_name = dnet.c2s_list[0].name
            config.c2s_mappings[c2s_name].responses = [
                S2CResponse(protocol="S2CUpdateHero", order=1, type="必然回包"),
                S2CResponse(protocol="S2CAddHero", order=2, type="按条件回包",
                           condition="如果英雄不存在")
            ]

        # 保存配置
        if manager.save_config(dnet.relative_path, config):
            print("配置保存成功")

        # 重新加载
        loaded = manager.load_config(dnet.relative_path)
        if loaded:
            print(f"配置加载成功: {loaded.dnet_file}")
            for c2s, mapping in loaded.c2s_mappings.items():
                print(f"  {c2s}: {len(mapping.responses)} 个响应")

        # 验证配置
        warnings = manager.validate_config(config, dnet, dnet_files)
        if warnings:
            print("验证警告:")
            for w in warnings:
                print(f"  - {w}")
        else:
            print("验证通过")
