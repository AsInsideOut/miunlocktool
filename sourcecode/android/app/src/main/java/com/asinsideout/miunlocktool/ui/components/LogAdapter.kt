package com.asinsideout.miunlocktool.ui.components

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.core.content.ContextCompat
import androidx.recyclerview.widget.RecyclerView
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.LogEntry

class LogAdapter : RecyclerView.Adapter<LogAdapter.LogViewHolder>() {

    private val logs = mutableListOf<LogEntry>()

    fun addLog(entry: LogEntry) {
        logs.add(entry)
        if (logs.size > 500) {
            logs.removeAt(0)
            notifyItemRemoved(0)
        }
        notifyItemInserted(logs.size - 1)
    }

    fun setLogs(newLogs: List<LogEntry>) {
        logs.clear()
        logs.addAll(newLogs)
        notifyDataSetChanged()
    }

    fun clear() {
        val count = logs.size
        logs.clear()
        notifyItemRangeRemoved(0, count)
    }

    fun getAllLogsText(): String {
        return logs.joinToString("\n") { "[${it.timestamp}] ${it.text}" }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LogViewHolder {
        val view = LayoutInflater.from(parent.context).inflate(R.layout.item_log, parent, false)
        return LogViewHolder(view)
    }

    override fun onBindViewHolder(holder: LogViewHolder, position: Int) {
        holder.bind(logs[position])
    }

    override fun getItemCount(): Int = logs.size

    class LogViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        private val tvLogLine: TextView = itemView.findViewById(R.id.tv_log_line)

        fun bind(entry: LogEntry) {
            tvLogLine.text = "[${entry.timestamp}] ${entry.text}"
            val colorRes = when (entry.colorType) {
                LogColorType.GREEN -> R.color.log_text_green
                LogColorType.CYAN -> R.color.log_text_cyan
                LogColorType.YELLOW -> R.color.log_text_yellow
                LogColorType.RED -> R.color.log_text_red
                LogColorType.PURPLE -> R.color.log_text_purple
                LogColorType.DEFAULT -> R.color.log_text_default
            }
            tvLogLine.setTextColor(ContextCompat.getColor(itemView.context, colorRes))
        }
    }
}

