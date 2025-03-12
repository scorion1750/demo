from fastapi import Request

def get_client_ip(request: Request) -> str:
    """
    获取客户端的真实 IP 地址
    
    尝试从各种 HTTP 头中获取，如果都不存在，则使用 request.client.host
    """
    # 常见的代理头
    headers_to_check = [
        'X-Forwarded-For',
        'X-Real-IP',
        'CF-Connecting-IP',  # Cloudflare
        'True-Client-IP'     # Akamai and Cloudflare
    ]
    
    for header in headers_to_check:
        if header in request.headers:
            # X-Forwarded-For 可能包含多个 IP，取第一个
            ips = request.headers[header].split(',')
            if ips:
                return ips[0].strip()
    
    # 如果没有代理头，使用直接连接的客户端 IP
    return request.client.host if request.client else "unknown" 