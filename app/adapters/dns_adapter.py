from collections.abc import Callable

import dns.exception
import dns.resolver


class DnsAdapter:
    """Адаптер DNS-запросов через `dnspython`."""
    def __init__(self, lifetime: float = 8.0) -> None:
        """
        Args:
            lifetime: Общий таймаут резолвера в секундах.
        """
        self.lifetime = lifetime

    def resolve_bundle(self, domain: str) -> dict[str, list[str]]:
        """
        Возвращает набор записей A, AAAA, CNAME и MX для имени.

        Args:
            domain: Доменное имя без схемы и без пути.

        Returns:
            Словарь с ключами `a`, `aaaa`, `cname`, `mx` и списками строк.
        """
        resolver = dns.resolver.Resolver()
        resolver.lifetime = self.lifetime

        return {
            "a": self.resolve_type(resolver, domain, "A", lambda r: str(r)),
            "aaaa": self.resolve_type(resolver, domain, "AAAA", lambda r: str(r)),
            "cname": self.resolve_type(resolver, domain, "CNAME", lambda r: str(r.target).rstrip(".")),
            "mx": self.resolve_type(
                resolver,
                domain,
                "MX",
                lambda r: f"{r.preference} {str(r.exchange).rstrip('.')}",
            ),
        }

    def resolve_type(
        self,
        resolver: dns.resolver.Resolver,
        domain: str,
        rtype: str,
        serialize: Callable[[object], str],
    ) -> list[str]:
        """
        Безопасно читает записи одного типа.

        Args:
            resolver: Настроенный резолвер.
            domain: Имя зоны.
            rtype: Тип записи (`A`, `AAAA`, и т.д.).
            serialize: Функция преобразования `rdata` в строку.

        Returns:
            Список строк; пустой при отсутствии данных или ошибке резолвинга.
        """
        try:
            answer = resolver.resolve(domain, rtype)
        except (
            dns.resolver.NXDOMAIN,
            dns.resolver.NoAnswer,
            dns.resolver.NoNameservers,
            dns.exception.Timeout,
            dns.resolver.LifetimeTimeout,
        ):
            return []

        out: list[str] = []

        for rdata in answer:
            out.append(str(serialize(rdata)))

        return out
