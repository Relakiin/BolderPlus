def toggle_bold(service, document_id, words, bold=True, ignore_case=False):
    """Toggle bold formatting for the specified words in the Google Document."""
    doc = service.documents().get(documentId=document_id).execute()
    requests = []
    changes_count = 0  # Counter for the number of changes made

    # Normalize words for case-insensitive matching
    normalized_words = [word.lower() if ignore_case else word for word in words]

    # Iterate through the document's content
    for element in doc['body']['content']:
        if 'paragraph' in element:
            for paragraph_element in element['paragraph']['elements']:
                if 'textRun' in paragraph_element and 'content' in paragraph_element['textRun']:
                    text = paragraph_element['textRun']['content']
                    normalized_text = text.lower() if ignore_case else text

                    for word, normalized_word in zip(words, normalized_words):
                        start_index = 0
                        while True:
                            # Find the word in the text
                            start_index = normalized_text.find(normalized_word, start_index)
                            if start_index == -1:
                                break

                            # Ensure it's a whole word match
                            before = start_index - 1
                            after = start_index + len(normalized_word)
                            if (before >= 0 and normalized_text[before].isalnum()) or \
                               (after < len(normalized_text) and normalized_text[after].isalnum()):
                                start_index += len(normalized_word)
                                continue

                            # Add the request to bold the word
                            end_index = start_index + len(normalized_word)
                            requests.append({
                                'updateTextStyle': {
                                    'range': {
                                        'startIndex': paragraph_element['startIndex'] + start_index,
                                        'endIndex': paragraph_element['startIndex'] + end_index
                                    },
                                    'textStyle': {
                                        'bold': bold
                                    },
                                    'fields': 'bold'
                                }
                            })
                            changes_count += 1  # Increment the counter
                            start_index = end_index

    # Execute the batch update request
    if requests:
        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    return changes_count  # Return the number of changes made