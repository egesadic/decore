def newslideshow(dly, forceMode, filesArray, delaysMap):
    try:
        global HAS_MEDIA

        # Create file manifest.
        filelist = [f for f in listdir(MEDIA_PATH) if isfile(join(MEDIA_PATH, f))]

        printmessage("Files in order:" + str(filesArray))

        existingFilesInOrder = filelist
        if forceMode == True and len(filelist) >= len(filesArray):
            existingFilesInOrder = []
            for f1 in filesArray:
                doesExist = False
                for f2 in filelist:
                    if f1 == f2:
                        doesExist = True
                        break
                if doesExist == True:
                    existingFilesInOrder.append(f1)

        printmessage("Found " + str(len(existingFilesInOrder)) + " items: " + ' '.join(existingFilesInOrder) + " ")

        # If filelist is empty, print a message that indicates no media was found on the node.
        if not existingFilesInOrder:
            HAS_MEDIA = False
            emptymedia()
        else:
            os.system("killall -9 fbi")
            HAS_MEDIA = True
            # Check whether there are videos in current media.
            # Images will be played ONCE if there are any video.
            isonce = ""
            for file in existingFilesInOrder:
                if file.endswith(VIDEO_EXT):
                    isonce = " -once "
                    break

            # Definition of variables used in function.
            name = "slide.dpa"
            filepath = SLIDE_PATH + name
            # isRandom = bool(rnd)
            delay = str(dly) + " "
            imgCount = 0
            imgList = []
            vidCount = 0
            vidName = ""
            temp = ""

            # Script bodies that will be used while creating the slide.
            fullscript = "#!/bin/bash\ncd " + MEDIA_PATH + "\nwhile true;\ndo\n"
            imgScript = "clear\nfbi --noverbose -a -t " + delay + isonce
            vidScript = "clear\nomxplayer " + MEDIA_PATH

            # Delay cannot be zero. 15 seconds is the default interval value.
            if str(dly) is "0":
                printmessage("Invalid or unspecified delay interval, assuming a 15 seconds interval")
                delay = str(15)

            # Files are randomized in order if the RANDOM flag was set.
            ''' if isRandom:
                printmessage("Random flag was on, randomizing file list...", 0.1)
                shuffle(existingFilesInOrder)
                printmessage("Randomized list: " + ''.join(existingFilesInOrder) + "\n") '''

            # Beginning of the slide creation.
            for file in existingFilesInOrder:
                printmessage("Now processing file: " + file)
                printmessage("current status: ImageCount=" + str(imgCount) + " VidCount=" + str(vidCount) + "\n")

                currentFileDelay = delay  # Will hold delay for current file

                if forceMode == True:
                    if delaysMap[file] != None and delaysMap[file] != 0:
                        currentFileDelay = str(delaysMap[file])
                        printmessage("Current file's delay is: " + currentFileDelay)

                if imgCount == vidCount:
                    if file.endswith(IMAGE_EXT):
                        # printmessage("first media is an image, combo started...\n", 0.1)
                        imgList.append(str(file).replace(' ', "\\ ") + " ")
                        imgCount += 1
                        # printmessage("img's appended to list, continuing process...\n", 0.1)
                    elif file.endswith(VIDEO_EXT):
                        # printmessage("first media is a video, writing to bash file...\n", 0.1)
                        vidName = ''.join(
                            [fullscript, vidScript, str(file).replace(' ', "\\ "), " >/dev/null 2>&1", '\n'])
                        fullscript = vidName
                        vidCount += 1
                    else:
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")

                # image list generator, break the combo if the next media in line isnt an
                elif imgCount > vidCount:
                    if file.endswith(IMAGE_EXT):
                        printmessage("image combo ongoing, populating image array...")
                        imgList.append(str(file).replace(' ', "\\ ") + " ")
                        imgCount += 1
                        printmessage("Current combo: " + ''.join(imgList))
                    elif file.endswith(VIDEO_EXT):
                        printmessage("combo broken!")
                        imgCount = 0
                        combinedImg = "".join(imgList)
                        fullscript = ''.join(
                            [fullscript, imgScript, combinedImg, '\n', vidScript, str(file).replace(' ', "\\ "),
                             " >/dev/null 2>&1", '\n'])
                        vidCount += 1
                    else:
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")

                elif vidCount > imgCount:
                    if file.endswith(VIDEO_EXT):
                        temp = ''.join([fullscript, vidScript, str(file).replace(' ', "\\ "), " >/dev/null 2>&1", '\n'])
                        fullscript = temp
                        vidCount += 1
                    elif file.endswith(IMAGE_EXT):
                        printmessage("img combo started...")
                        vidCount = 0
                        imgList = []
                        imgList.append(str(file).replace(' ', "\\ ") + " ")
                        imgCount += 1
                    else:
                        printmessage("File " + file + "has an unknown (or undefined) file format.", "warning")

            if len(imgList) > 0:
                printmessage(
                    str(len(imgList)) + " images left in array after end of operation, writing them to file...")
                combinedImg = ''.join(imgList)
                fullscript = ''.join([fullscript, imgScript, combinedImg, " >/dev/null 2>&1", '\n'])
                printmessage("Done writing remainder files...\n")

            f = open(SLIDE_PATH + name, 'w')
            f.write(fullscript + "done\nexit 0")
            f.close()

            os.system("chmod +x " + filepath)
            printmessage("Success! Slideshow " + name + " has been successfully created under " + filepath + ".",
                         "info")

    except Exception as e:
        printmessage("Aborted slide creation.\nReason was: " + e, "exception")
        if os.path.exists(filepath):
            printmessage("Removing incomplete slide file...", "warning")
            slide.close()
            os.remove(filepath)
            printmessage("Removed file successfully.", "warning")
    except SystemExit as ex:
        printmessage(ex, "warning")
