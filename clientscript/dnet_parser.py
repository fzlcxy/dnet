"""
.dnet文件解析模块 - 支持新格式
"""
import os
import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Field:
    """协议字段"""
    name: str
    type_info: str
    description: str


@dataclass
class Protocol:
    """单个协议"""
    name: str
    description: str
    fields: List[Field] = field(default_factory=list)


@dataclass
class DnetFile:
    """解析后的.dnet文件"""
    file_path: str
    file_name: str
    relative_path: str
    description: str
    c2s_module: str
    s2c_module: str
    version: str = ""
    c2s_list: List[Protocol] = field(default_factory=list)
    s2c_list: List[Protocol] = field(default_factory=list)

    def has_c2s(self) -> bool:
        return len(self.c2s_list) > 0

    def has_s2c(self) -> bool:
        return len(self.s2c_list) > 0


class DnetParser:
    """解析.dnet协议文件（新格式）"""

    def parse_file(self, file_path: str, proto_root: str = "") -> Optional[DnetFile]:
        """解析单个.dnet文件"""
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_name = os.path.basename(file_path)
        if proto_root:
            relative_path = os.path.relpath(file_path, proto_root)
        else:
            relative_path = file_name

        dnet = DnetFile(
            file_path=file_path,
            file_name=file_name,
            relative_path=relative_path,
            description="",
            c2s_module="",
            s2c_module=""
        )

        lines = content.split('\n')
        current_section = None  # 'C2S' or 'S2C'
        current_protocol = None
        in_forlist = False  # 是否在forlist块中

        for line in lines:
            line_stripped = line.strip()

            # 跳过空行和注释
            if not line_stripped or line_stripped.startswith('#'):
                continue

            # 解析头部信息 - VERSION
            if line_stripped.startswith('VERSION'):
                match = re.match(r'VERSION[：:]\s*(.+)', line_stripped)
                if match:
                    dnet.version = match.group(1).strip()
                continue

            # 解析头部信息 - DESC
            if line_stripped.startswith('DESC'):
                match = re.match(r'DESC[：:]\s*(.+)', line_stripped)
                if match:
                    dnet.description = match.group(1).strip()
                continue

            # 解析头部信息 - CMODULE (C2S模块)
            if line_stripped.startswith('CMODULE'):
                match = re.match(r'CMODULE[：:]\s*(.+)', line_stripped)
                if match:
                    dnet.c2s_module = match.group(1).strip()
                continue

            # 解析头部信息 - SMODULE (S2C模块)
            if line_stripped.startswith('SMODULE'):
                match = re.match(r'SMODULE[：:]\s*(.+)', line_stripped)
                if match:
                    dnet.s2c_module = match.group(1).strip()
                continue

            # 解析GS2C段落开始（S2C协议）
            if line_stripped.startswith('GS2C:'):
                current_section = 'S2C'
                current_protocol = None
                in_forlist = False
                continue

            # 解析C2GS段落开始（C2S协议）
            if line_stripped.startswith('C2GS:'):
                current_section = 'C2S'
                current_protocol = None
                in_forlist = False
                continue

            # 解析forlist开始（嵌套结构，暂时跳过内部字段）
            if line_stripped.startswith('forlist '):
                in_forlist = True
                continue

            # forlist内部的字段（缩进更深），暂时跳过
            if in_forlist and line.startswith('\t\t\t'):
                continue
            else:
                in_forlist = False

            # 解析协议定义（新格式：1:C2SUpdateHeroName:更新英雄名称）
            protocol_match = re.match(r'^(\d+):([A-Za-z0-9_]+):(.+)$', line_stripped)
            if protocol_match and current_section:
                protocol_name = protocol_match.group(2)
                protocol_desc = protocol_match.group(3)
                current_protocol = Protocol(
                    name=protocol_name,
                    description=protocol_desc
                )
                if current_section == 'C2S':
                    dnet.c2s_list.append(current_protocol)
                else:
                    dnet.s2c_list.append(current_protocol)
                continue

            # 解析字段（新格式：iHeroID,4,英雄ID）
            field_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*),([^,]+),(.+)$', line_stripped)
            if field_match and current_protocol:
                field_name = field_match.group(1)
                field_type = field_match.group(2)
                field_desc = field_match.group(3)
                current_protocol.fields.append(Field(
                    name=field_name,
                    type_info=field_type,
                    description=field_desc
                ))

        return dnet

    def scan_directory(self, proto_dir: str) -> List[DnetFile]:
        """递归扫描proto目录下所有.dnet文件"""
        result = []

        if not os.path.exists(proto_dir):
            return result

        for root, dirs, files in os.walk(proto_dir):
            for file in files:
                if file.endswith('.dnet'):
                    file_path = os.path.join(root, file)
                    dnet = self.parse_file(file_path, proto_dir)
                    if dnet:
                        result.append(dnet)

        # 按相对路径排序
        result.sort(key=lambda x: x.relative_path)
        return result


if __name__ == '__main__':
    # 测试代码
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proto_dir = os.path.join(os.path.dirname(script_dir), 'proto')

    parser = DnetParser()
    dnet_files = parser.scan_directory(proto_dir)

    for dnet in dnet_files:
        print(f"\n=== {dnet.relative_path} ===")
        print(f"版本: {dnet.version}")
        print(f"描述: {dnet.description}")
        print(f"C2S模块: {dnet.c2s_module}")
        print(f"S2C模块: {dnet.s2c_module}")
        print(f"C2S协议 ({len(dnet.c2s_list)}):")
        for p in dnet.c2s_list:
            print(f"  - {p.name}: {p.description}")
            for f in p.fields:
                print(f"      {f.name} ({f.type_info}): {f.description}")
        print(f"S2C协议 ({len(dnet.s2c_list)}):")
        for p in dnet.s2c_list:
            print(f"  - {p.name}: {p.description}")
            for f in p.fields:
                print(f"      {f.name} ({f.type_info}): {f.description}")
