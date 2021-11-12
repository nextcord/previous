import os

def split_txtfile(in_filename: str, chunk_len=4000) -> list:
    """Takes a long plaintext file from the assets directory and splits it up
    into 4000 character-long chunks to be sent over Discord and stay under the
    embed content character limit (which is actually 4096 but shhh).
    """
    in_file_fullpath = os.path.join(os.getcwd(), "assets", in_filename)
    all_chunks = []  # Each item is a <4000-character-long chunk of the infile.
    current_chunk = ""  #  Store temp chunks here before adding to the above.
    
    with open(in_file_fullpath) as in_file:
        for line in in_file:
            # Before we concatenate the current chunk and the current line, we
            # need to check if the resulting chunk is over 4000 chars long.
            # If so, add that chunk to the list of chunks and start a brand new
            # chunk to add to.
            if len(current_chunk + line) >= chunk_len:
                all_chunks.append(current_chunk)
                current_chunk = ""
            current_chunk += line
        
        # Once we finish iterating over each line in the input file, the last
        # chunk is probably gonna be under 4000 chars and therefore won't be
        # added to the chunk list. We have to add it here in case that happens.
        all_chunks.append(current_chunk)
    return all_chunks

