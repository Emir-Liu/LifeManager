from calendar_engine.core.interface import CalendarProvider


class CalendarProviderFactory:
    """日历提供者工厂"""
    
    _providers = {}
    
    @classmethod
    def register(cls, provider_type: str, provider_class: type):
        """注册日历提供者
        
        Args:
            provider_type: 提供者类型标识
            provider_class: 提供者类
        """
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create(cls, provider_type: str, config: dict = None) -> CalendarProvider:
        """创建日历提供者实例
        
        Args:
            provider_type: 提供者类型 (google/outlook/apple)
            config: 配置字典
            
        Returns:
            CalendarProvider实例
            
        Raises:
            ValueError: 如果提供者类型不支持
        """
        config = config or {}
        provider_class = cls._providers.get(provider_type)
        
        if not provider_class:
            raise ValueError(f"Unsupported provider: {provider_type}")
        
        return provider_class(**config)
    
    @classmethod
    def list_providers(cls) -> list:
        """列出所有已注册的提供者"""
        return list(cls._providers.keys())
    
    @classmethod
    def create_manager(cls, provider_configs: dict) -> 'CalendarManager':
        """创建多日历管理器
        
        Args:
            provider_configs: 提供者配置字典,格式为 {'google': {...}, 'outlook': {...}}
            
        Returns:
            CalendarManager实例
        """
        from calendar_engine.core.manager import CalendarManager
        
        providers = {}
        for provider_type, config in provider_configs.items():
            providers[provider_type] = cls.create(provider_type, config)
        
        return CalendarManager(providers)
