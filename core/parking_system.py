# core/parking_system.py
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any

class ParkingSystem:
    """管理停车场的业务逻辑，如车辆进出、计费等"""
    def __init__(self, total_spots: int = 100):
        self.total_spots = total_spots
        self.db_path = 'parking.db'

    def _get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)

    def get_available_spots(self) -> int:
        """计算当前可用的停车位数量"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            occupied = cursor.execute(
                "SELECT COUNT(*) FROM parking_records WHERE exit_time IS NULL"
            ).fetchone()[0]
        return self.total_spots - occupied

    def vehicle_entry(self, plate_number: str) -> Optional[int]:
        """
        处理车辆入场，分配一个车位号。
        如果车位已满，返回None。
        """
        if self.get_available_spots() <= 0:
            return None

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 查找所有已被占用的车位
            occupied_spots = {row[0] for row in cursor.execute(
                "SELECT spot_number FROM parking_records WHERE exit_time IS NULL"
            ).fetchall()}
            
            # 从1号车位开始，找到第一个未被占用的车位
            spot_number = next((i for i in range(1, self.total_spots + 1) if i not in occupied_spots), None)

            if spot_number:
                cursor.execute(
                    "INSERT INTO parking_records (plate_number, entry_time, spot_number) VALUES (?, ?, ?)",
                    (plate_number, datetime.now(), spot_number)
                )
                conn.commit()
            return spot_number

    def calculate_fee(self, minutes: float) -> float:
        """根据停车分钟数计算费用"""
        hours = minutes / 60
        if hours <= 1:
            return 15.0
        # 超过1小时后，每小时10元
        return 15.0 + (hours - 1) * 10.0

    def vehicle_exit(self, plate_number: str) -> Optional[Dict[str, Any]]:
        """
        处理车辆出场，计算费用并更新数据库。
        返回包含费用和停车时长的字典，如果找不到车辆则返回None。
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            record = cursor.execute(
                "SELECT id, entry_time FROM parking_records WHERE plate_number = ? AND exit_time IS NULL",
                (plate_number,)
            ).fetchone()

            if not record:
                return None

            record_id, entry_time_str = record
            entry_time = datetime.strptime(entry_time_str, '%Y-%m-%d %H:%M:%S.%f')
            exit_time = datetime.now()
            
            duration_seconds = (exit_time - entry_time).total_seconds()
            fee = self.calculate_fee(duration_seconds / 60)

            cursor.execute(
                "UPDATE parking_records SET exit_time = ?, fee = ? WHERE id = ?",
                (exit_time, fee, record_id)
            )
            conn.commit()
            
            return {"fee": fee, "duration_minutes": duration_seconds / 60}

    def get_vehicle_history(self, plate_number: str) -> List[tuple]:
        """获取特定车辆的所有历史停车记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute(
                "SELECT entry_time, exit_time, fee, spot_number FROM parking_records WHERE plate_number = ? ORDER BY entry_time DESC",
                (plate_number,)
            ).fetchall()

    def is_vehicle_inside(self, plate_number: str) -> bool:
        """检查车辆当前是否在停车场内"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            record = cursor.execute(
                "SELECT id FROM parking_records WHERE plate_number = ? AND exit_time IS NULL",
                (plate_number,)
            ).fetchone()
        return record is not None