import re
import json
import logging

logger = logging.getLogger("nex-parser")

class PlannerParser:
    @staticmethod
    def parse_action(output: str):
        try:
            # 1. Clean output from common markdown decorations but keep internal structure
            clean_output = output.replace("**", "")
            
            # 2. Try to find ACTION/AKSI block with DOTALL to handle multiline
            match = re.search(
                r"(ACTION|AKSI|NEXT ACTION|📝 NEXT ACTION):\s*([\w\s_]+)\s*\((.*?)\)", 
                clean_output, 
                re.IGNORECASE | re.DOTALL
            )
            
            if not match:
                # 2.1 FALLBACK: Check if LLM outputted JSON instead
                json_match = re.search(r"(\{.*\})", clean_output.replace("\n", " "), re.DOTALL)
                if json_match:
                    try:
                        data = json.loads(json_match.group(1))
                        name = data.get("action") or data.get("tool") or data.get("skill")
                        args = data.get("parameters") or data.get("args") or data.get("params") or {}
                        if not args:
                            args = {k: v for k, v in data.items() if k not in ["action", "tool", "skill"]}
                        if name:
                            return name.strip().lower(), args
                    except:
                        pass
                return None, None
                
            name = match.group(2).strip().lower().replace(" ", "_")
            params_str = match.group(3).strip()
            
            # 3. Robust parameter extraction (KV Pair)
            pattern = r'(\w+)\s*=\s*(?:["\'](.*?)["\']|([^,\s\)]+))'
            pairs = re.findall(pattern, params_str, re.DOTALL)
            
            args = {}
            for k, q_v, u_v in pairs:
                val = (q_v if q_v is not None else u_v).strip()
                args[k] = val.strip('`').strip('"').strip("'")
                
            # 3.1 FALLBACK: If no KV pairs found, try positional split
            if not args and params_str:
                parts = [p.strip().strip('`').strip('"').strip("'") for p in params_str.split(",")]
                if name == "schedule_zoom_meeting":
                    if len(parts) >= 1: args["topic"] = parts[0]
                    if len(parts) >= 2: args["datetime_iso"] = parts[1]
                elif name == "search_knowledge":
                    if len(parts) >= 1: args["query"] = parts[0]
                elif name == "finish":
                    args["answer"] = params_str.strip('`').strip('"').strip("'")

            # 4. Handle finish(answer="...") specific cases
            if name == "finish" and not args and params_str:
                args = {"answer": params_str.strip('`').strip('"').strip("'")}
                
            # 5. Smart mapping for hallucinated param names (Non-Destructive)
            if "start_time" in args and "datetime_iso" not in args:
                args["datetime_iso"] = args["start_time"]
            elif "datetime_iso" in args and "start_time" not in args:
                args["start_time"] = args["datetime_iso"]
                
            if "query" not in args and name == "search_knowledge" and params_str:
                args["query"] = params_str.strip('`').strip('"').strip("'")
                
            return name, args
        except Exception as e:
            logger.error(f"[PLANNER] Parse Error: {str(e)}")
            return None, None


