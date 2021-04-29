# 128 ASCII values available
action = [None] * 128
action_statements = []

action[32] = "BREAK"                                            # Spacebar
action_statements.append("Press Spacebar to BRAEK the process.")

action[65] = action[97] = "ADD_LAYER"                           # 'a' , 'A'
action_statements.append("Press 'A' to ADD NEW LAYER.")

action[76] = action[108] = "SHOW_SELECTED_LAYERS"               # 'l' , 'L'
action_statements.append("Press 'L' to SHOW SPECIFIC LAYERS.")

action[12] = "LAYER_PROCESSES"                                  # Ctrl + L
action_statements.append("Press 'Ctrl + L' to see all the layer processes available(Rearrane Layers).")