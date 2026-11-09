gm-a items:
1 Identifies "No watermarks" wording as likely refusal trigger with references; removes it
2 Says empty text + zero files is typically content-filter/refusal and to log finishReason
3 Adds retry of empty responses before throwing, with finishReason in error
4 Puts reference images before text part
5 Says do not describe contents of the supplied screenshot in the prompt (blue bar chart, "Sales" title)
6 Selects image via files.find(mediaType startsWith image/) not files[0]
7 Adds imageConfig aspectRatio/size or notes it optional; does not invent wrong API
8 Notes small text on screens may be garbled (check output)
