# 128 ASCII values available
action = [None] * 128
action_statements = []

action[32] = "BREAK"                                            # Spacebar
action_statements.append("Press Spacebar to BRAEK the process.")

action[65] = action[97] = "ADD_LAYER"                           # 'a' , 'A'
action_statements.append("Press 'A' to ADD NEW LAYER.")
