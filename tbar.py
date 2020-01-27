from bar import SimpleProgressBar

b1 = SimpleProgressBar(47)
b1.update()
b1.status = 'Done...'
b1.processed = 20
b1.update()
# b1.done()