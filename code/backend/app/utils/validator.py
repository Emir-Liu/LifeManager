"""
数据验证工具模块
提供常用的数据验证函数
"""
import re
from typing import Optional, List, Any
from datetime import datetime, date


class ValidationError(Exception):
    """验证错误异常"""
    pass


class Validator:
    """数据验证器"""

    @staticmethod
    def validate_username(username: str) -> bool:
        """
        验证用户名

        规则:
        - 长度3-50字符
        - 只包含字母、数字、下划线
        - 必须以字母开头

        Args:
            username: 用户名

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if not username:
            raise ValidationError("用户名不能为空")

        if len(username) < 3 or len(username) > 50:
            raise ValidationError("用户名长度必须在3-50字符之间")

        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
            raise ValidationError("用户名只能包含字母、数字和下划线，且必须以字母开头")

        return True

    @staticmethod
    def validate_email(email: Optional[str]) -> bool:
        """
        验证邮箱地址

        Args:
            email: 邮箱地址

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if not email:
            return True  # 邮箱可选

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("邮箱地址格式不正确")

        return True

    @staticmethod
    def validate_password(password: str) -> bool:
        """
        验证密码强度

        规则:
        - 长度至少6字符
        - 建议包含字母和数字

        Args:
            password: 密码

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if not password:
            raise ValidationError("密码不能为空")

        if len(password) < 6:
            raise ValidationError("密码长度至少6字符")

        return True

    @staticmethod
    def validate_title(title: str, min_len: int = 1, max_len: int = 200) -> bool:
        """
        验证标题

        Args:
            title: 标题
            min_len: 最小长度
            max_len: 最大长度

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if not title:
            raise ValidationError("标题不能为空")

        if len(title) < min_len or len(title) > max_len:
            raise ValidationError(f"标题长度必须在{min_len}-{max_len}字符之间")

        return True

    @staticmethod
    def validate_description(description: Optional[str], max_len: int = 5000) -> bool:
        """
        验证描述

        Args:
            description: 描述
            max_len: 最大长度

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if description and len(description) > max_len:
            raise ValidationError(f"描述长度不能超过{max_len}字符")

        return True

    @staticmethod
    def validate_date_range(start_date: date, end_date: Optional[date] = None) -> bool:
        """
        验证日期范围

        Args:
            start_date: 开始日期
            end_date: 结束日期（可选）

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if start_date < date.today():
            raise ValidationError("开始日期不能早于今天")

        if end_date and end_date < start_date:
            raise ValidationError("结束日期不能早于开始日期")

        return True

    @staticmethod
    def validate_status(status: str, valid_statuses: List[str]) -> bool:
        """
        验证状态值

        Args:
            status: 状态值
            valid_statuses: 有效的状态列表

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if status not in valid_statuses:
            raise ValidationError(f"状态必须是以下值之一: {', '.join(valid_statuses)}")

        return True

    @staticmethod
    def validate_id(id_value: Any) -> bool:
        """
        验证ID

        Args:
            id_value: ID值

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if id_value is None:
            raise ValidationError("ID不能为空")

        if not isinstance(id_value, int) or id_value <= 0:
            raise ValidationError("ID必须是正整数")

        return True

    @staticmethod
    def validate_json_content(content: str) -> bool:
        """
        验证JSON格式内容

        Args:
            content: JSON字符串

        Returns:
            验证是否通过

        Raises:
            ValidationError: 验证失败
        """
        if not content:
            raise ValidationError("内容不能为空")

        try:
            import json
            json.loads(content)
        except json.JSONDecodeError as e:
            raise ValidationError(f"JSON格式不正确: {str(e)}")

        return True


# 便捷函数
def validate_user_input(username: str, password: str, email: Optional[str] = None) -> bool:
    """
    验证用户输入

    Args:
        username: 用户名
        password: 密码
        email: 邮箱（可选）

    Returns:
        验证是否通过
    """
    Validator.validate_username(username)
    Validator.validate_password(password)
    if email:
        Validator.validate_email(email)
    return True
