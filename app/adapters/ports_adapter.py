import socket
from concurrent.futures import ThreadPoolExecutor, as_completed


class PortsAdapter:
    """Проверка TCP-портов на доступность (connect)."""
    def __init__(self, connect_timeout: float = 0.45, max_workers: int = 32) -> None:
        """
        Args:
            connect_timeout: Таймаут попытки на порт в секундах.
            max_workers: Размер пула потоков при сканировании списка портов.
        """
        self.connect_timeout = connect_timeout
        self.max_workers = max_workers

    def probe_ports(self, host: str, ports: list[int]) -> list[dict[str, object]]:
        """
        Параллельно проверяет список портов на хосте.

        Args:
            host: Имя хоста или IP.
            ports: Набор портов для проверки.

        Returns:
            Список словарей `port`, `open`, опционально `error` при сбое сокета.
        """
        unique_ports = sorted({p for p in ports if 0 < p < 65536})
        results: list[dict[str, object]] = []

        if not unique_ports:
            return results

        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(unique_ports))) as pool:
            future_map = {pool.submit(self.is_port_open, host, port): port for port in unique_ports}

            for future in as_completed(future_map):
                port = future_map[future]

                try:
                    is_open, err = future.result()
                except Exception as exc:
                    is_open, err = False, str(exc)

                row: dict[str, object] = {"port": port, "open": is_open}

                if err:
                    row["error"] = err

                results.append(row)

        results.sort(key=lambda item: int(item["port"]))

        return results

    def is_port_open(self, host: str, port: int) -> tuple[bool, str | None]:
        """
        Пытается установить TCP-соединение с `host:port`.

        Args:
            host: Имя хоста или IP.
            port: Номер порта.

        Returns:
            Пара (`True` если порт принимает соединение, текст ошибки или `None`).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.connect_timeout)

        try:
            sock.connect((host, port))
        except OSError as exc:
            return False, str(exc)
        else:
            return True, None
        finally:
            sock.close()
