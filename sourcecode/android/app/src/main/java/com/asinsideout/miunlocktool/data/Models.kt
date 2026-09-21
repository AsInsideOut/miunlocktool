package com.asinsideout.miunlocktool.data

enum class AccountStatus {
    NOT_CHECKED,
    CHECKING,
    READY,
    APPROVED,
    BLOCKED,
    TOO_NEW,
    EXPIRED,
    ERROR,
    UNKNOWN
}

data class CheckStatusResult(
    val status: AccountStatus,
    val message: String,
    val deadline: String? = null
)

data class ApplyResult(
    val code: Int,
    val applyResult: Int?,
    val message: String,
    val isSuccess: Boolean,
    val deadline: String? = null
)

data class LogEntry(
    val timestamp: String,
    val text: String,
    val colorType: LogColorType = LogColorType.DEFAULT
)

enum class LogColorType {
    DEFAULT,
    GREEN,
    CYAN,
    YELLOW,
    RED,
    PURPLE
}

enum class ExecutionMode(val id: Int) {
    MANUAL(0),
    AUTO(1)
}

