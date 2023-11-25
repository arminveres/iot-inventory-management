def log_time_to_file(analysis_type: str, line: str):
    """
    write `line` to performance log file
    """
    if analysis_type == 'issue':
        file_path = "./.agent_cache/issue_time_log"
    elif analysis_type == "update":
        file_path = "./.agent_cache/update_time_log"
    elif analysis_type == 'revocation':
        file_path = "./.agent_cache/revoc_time_log"

    with open(file_path, mode="a", encoding="utf-8") as log:
        log.write(line)
