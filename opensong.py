#------------ Start Build OpenSong Set function - last updated 03/02/2021 by Steve Rogers
import filelist                 #--- definition of list of files and directories used in the proces
import os
import getdatetime
import writehtml                #--- my module to create the HTML page with the bulletin info for the "livestream" page
import subprocess               #--- for launching external shell commands

#------------ Start Assemble Set function -  
def assembleset():
    import xml.etree.ElementTree as ET

    #-------------- Get the set name form the setname file -----------------------------
    textFile = open(filelist.SetFilename, 'r', encoding='utf-8',errors='ignore') #--- read the file containing the selected Set name
    XMLsetName = textFile.readline()              #--- read the first line from the file
    textFile.close()

    #-------------- Open the Template Set and load into XML document tree -----------------------------
    print('\nOpenSong.assembleset() Current Working Directory:', os.getcwd())
    os.chdir(filelist.setpath)   #-- change to the Sets directory
    print('\nOpenSong.assembleset() change working Directory to:', os.getcwd())
 
    datasource = open(XMLsetName, 'rb')
	 
    doctree = ET.parse(datasource)
    root = doctree.getroot()
    print('\nAssembleSet - the number of slide_groups in the set: ', len(root[0]))

    os.chdir(filelist.bulletinpath)   #-- switch back to the default Bulletins directory

    #-------------- call the process files function to process the files with the extracted bulletin information
    processfiles(doctree)                       #--- pass the XML set document tree
#------------ End Assemble Set function -  

#------------Start -  Process files with extracted bulletin information  
def processfiles(doctree):
    import xml.etree.ElementTree as ET
    import addnode
    import os

    #-------------- Read the contents of the Call To Worship text file -----------------------------
    textFile = open(filelist.CallToWorshipFileName, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.read()              #--- read the file into a string
    print('opensong.processfiles - call to worship body_text =', body_text)

    slide_group_name = 'Call to Worship'
    body_text = parsecalltoworship()        #--- call the 'parsecalltoworship' routine to separate the text into slides
    
    #addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function
    addnode.addbodyslides(doctree, slide_group_name, body_text) #--- call the add confession text function
    
    #-------------- Read the contents of the Bulletin Sermon  text file -----------------------------
    textFile = open(filelist.BulletinSermonFilename, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.read()              #--- read the file into a string
    #print(body_text)

    slide_group_name = 'Sermon'
    addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function

    #-- Add the Sermon Scripture to the XML document
    scripture = body_text.splitlines()
    scripture_ref = scripture[1].strip()
    print('\nOpenSong.processfiles - Sermon Scripture Reference=', scripture_ref)
    addnode.addscripture(doctree, slide_group_name, scripture_ref)

    #-------------- Read the contents of the Confession of Sin text file -----------------------------
    slide_group_name = 'Confession of Sin'
 
    textFile = open(filelist.ConfessionFilename, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.read()                 #--- read the confession of sin file into a string
    
    #--- strip the text at the 3rd ':' to remove the intro words
    char = ':'
    count = 3
    body_text = split_keep_after(body_text, char, count)
 
    #--- split the text based on period '.' 
    body_text = split_keep(body_text)           #--- call my function to split the string into lines, delimited by '.'
    #print('OpenSong.processfiles - body_text=', body_text)
    body_text.insert(0, slide_group_name)       #--- insert the title at the beginning of the list
    
    try:
        body_text.remove('.')                       #--- remove list element which is just a period
    except:
        pass

    addnode.addbodyslides(doctree, slide_group_name, body_text) #--- call the add body text function

    #-------------- Read the contents of the Assurance of Pardon text file -----------------------------
    textFile = open(filelist.AssuranceFilename, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.readlines()              #--- read the file into a list

    #print('\nAssurance of Pardon\n', body_text)
    #i = 0
    #for x in body_text:
    #    print('\ni=', i, 'x=', x)
    #    i +=1
 
    #-------------Modified Assurance of Pardon
    slide_group_name = 'Assurance of Pardon'
    scripture_ref = str(body_text[1].strip())
    print('\nScripture Reference:', scripture_ref)
    body_text = slide_group_name + '\n' + scripture_ref
    #print('\nBODY TEXT for Assurance of Pardon:\n', body_text)
    addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function

    addnode.addscripture(doctree, slide_group_name, scripture_ref)

    #-------------- Read the contents of the Affirmation of Faith text file -----------------------------
    textFile = open(filelist.AffirmationFileName, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.readlines()              #--- read the file into a list
    #print(body_text)

    slide_group_name = 'Affirmation of Faith'
    #addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function
    #--- split the text based on period '.' 
    #body_text = split_keep(body_text)           #--- call my function to split the string into lines, delimited by '.'
    #body_text.insert(0, slide_group_name)       #--- insert the title at the beginning of the list
    temp_text = body_text[0] + body_text[1]
    del body_text[1]              #--- remove the 1st and second list items
    del body_text[0]              #--- remove the 1st and second list items
    body_text.insert(0, temp_text)       #--- insert the title at the beginning of the list

    addnode.addbodyslides(doctree, slide_group_name, body_text) #--- call the add body text function    

    #-------------- Read the contents of the Scripture Reading text file -----------------------------
    textFile = open(filelist.ScriptureFileName, 'r', encoding='utf-8',errors='ignore')
    body_text = textFile.read()              #--- read the file into a string
    body_text = body_text + '\n'
    #print('\nScripture Reading body text=', body_text)

    slide_group_name = 'Scripture Reading'
    addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function

    #-- Add the Scripture Text to the XML document
    scripture = body_text.splitlines()
    scripture_ref = scripture[1].strip()
    #print('\nScripture Reference=', scripture_ref)
    addnode.addscripture(doctree, slide_group_name, scripture_ref)

    #-------------- Read the contents of the Announcements text file -----------------------------
    textFile = open(filelist.AnnouncementFileName, 'r', encoding='utf-8',errors='ignore')
    #body_text = textFile.read()              #--- read the file into a string
    body_text = textFile.readlines()              #--- read the file into a list

    #print(body_text)

    slide_group_name = 'Announcements'
    #addnode.addbodytext(doctree, slide_group_name, body_text) #--- call the addbodytext function
    addnode.addbodyslides(doctree, slide_group_name, body_text)

    #--- Process the Worship songs-----------------------------
    processsongs(doctree)
    
    #--- call the write xml set function to write the new xml set file
    writeXMLSet(doctree)

    #---- clean up the intermediary files after processing completes successfully
    cleanup()

    return()
#------------End -  Process files with extracted bulletin information  

#------------Start -  cleanup process i.e. rename files
def cleanup():
    import os
    import monitorfiles
    
    #--- clean up (or rename) the intermediate files to prepare for the next run
    if not os.path.isfile(filelist.PDFBulletinFilename):
        print("File {} does not exist. Wait for Discord post...".format(filelist.PDFBulletinFilename))
    else:
        os.replace(filelist.PDFBulletinFilename, filelist.OldPDFBulletinFilename)

    if not os.path.isfile(filelist.TextBulletinFilename ):
        print("File {} does not exist. Wait for Discord post...".format(filelist.TextBulletinFilename))
    else:
        os.replace(filelist.TextBulletinFilename , filelist.OldTextBulletinFilename)

    if not os.path.isfile(filelist.WorshipScheduleFilename):
        print("File {} does not exist. Wait for Discord post...".format(filelist.WorshipScheduleFilename))
    else:
        os.replace(filelist.WorshipScheduleFilename, filelist.OldWorshipScheduleFilename)

    if not os.path.isfile(filelist.AssuranceFilename):
        print("File {} does not exist. Wait for Discord post...".format(filelist.AssuranceFilename))
    else:
        os.replace(filelist.AssuranceFilename, filelist.OldAssuranceFilename)

    if not os.path.isfile(filelist.ConfessionFilename):
        print("File {} does not exist. Wait for Discord post...".format(filelist.ConfessionFilename))
    else:
         os.replace(filelist.ConfessionFilename, filelist.OldConfessionFilename)

    monitorfiles.filechecker()              #--- update the status file

    return()
#------------End  -  cleanup process

#------------Start -  Process Songs  
def processsongs(doctree):
    import xml.etree.ElementTree as ET
    import readworshipschedule
    import addnode

    #-------------- Read and process the songs text file -----------------------------
    readworshipschedule.readWS()        # read the worship schedule file extracted from discord and store in a  "lists" file
    songs = []

    with open(filelist.SongsFileName) as f:
        songs = f.read().splitlines()                   #read the songs.txt file into a list / array
   
    #--- process the Song of Approach
    song_name, presentation_order = songs[1].rsplit('-', 1) #split the line at '-'
    song_name = song_name.strip()                       #remove leading and trailing spaces
    presentation_order = presentation_order.strip()     #remove leading and trailing spaces

    slide_group_name = 'Song of Approach'
    body_text = slide_group_name
    body_text = body_text + '\n' + song_name

    #print('\nProcess Song of Approach - song name=', song_name, ' presentation order=', presentation_order)

    doctree = addnode.addsong(doctree, slide_group_name, song_name, presentation_order)   # (slide_group_name, song_name)
    addnode.addbodytext(doctree, slide_group_name, body_text)

    #--- process the Song of Response - last line in the list
    song_name, presentation_order = songs[len(songs)-1].rsplit('-', 1) #split the line at '-'
    song_name = song_name.strip()                       #remove leading and trailing spaces
    presentation_order = presentation_order.strip()     #remove leading and trailing spaces

    slide_group_name = 'Song of Response'
    body_text = slide_group_name
    body_text = body_text + '\n' + song_name

    #print('\nProcess Song of Response - song name=', song_name, ' presentation order=', presentation_order)

    doctree = addnode.addsong(doctree, slide_group_name, song_name, presentation_order)   # (slide_group_name, song_name)
    addnode.addbodytext(doctree, slide_group_name, body_text)

    #--- process Praise Songs - order is based on the established set name
    #-------------- Get the set name form the setname file -----------------------------
    textFile = open(filelist.SetFilename, 'r', encoding='utf-8',errors='ignore') #--- read the file containing the selected Set name
    XMLsetName = textFile.readline()              #--- read the first line from the file
    textFile.close()

    if 'No Gloria Patri' in XMLsetName:         # means use 1 song of praise and a song of assurance
        song_name, presentation_order = songs[2].rsplit('-', 1) #split the line at '-'
        song_name = song_name.strip()                       #remove leading and trailing spaces
        presentation_order = presentation_order.strip()     #remove leading and trailing spaces

        slide_group_name = 'Song of Praise'
        body_text = slide_group_name
        body_text = body_text + '\n' + song_name

        #print('\nProcess Song of Praise - song name=', song_name, ' presentation order=', presentation_order)

        doctree = addnode.addsong(doctree, slide_group_name, song_name, presentation_order)   # (slide_group_name, song_name)
        addnode.addbodytext(doctree, slide_group_name, body_text)

        #--- Song or Assurance
        song_name, presentation_order = songs[3].rsplit('-', 1) #split the line at '-'
        song_name = song_name.strip()                       #remove leading and trailing spaces
        presentation_order = presentation_order.strip()     #remove leading and trailing spaces

        slide_group_name = 'Song of Assurance'
        body_text = slide_group_name
        body_text = body_text + '\n' + song_name

        #print('\nProcess Song of Assurance - song name=', song_name, ' presentation order=', presentation_order)

        doctree = addnode.addsong(doctree, slide_group_name, song_name, presentation_order)   # (slide_group_name, song_name)
        addnode.addbodytext(doctree, slide_group_name, body_text)

    else:                           #--- process body_text for 2 Songs of Praise
        slide_group_name = 'Songs of Praise'
        body_text = slide_group_name

        for s in range(2, len(songs)-1):        #--- process body_text for 2 Songs of Praise
            song_name, presentation_order = songs[s].rsplit('-', 1) #split the line at '-'
            song_name = song_name.strip()                       #remove leading and trailing spaces
            presentation_order = presentation_order.strip()     #remove leading and trailing spaces
            body_text = body_text + '\n' + song_name

            #print('\nProcess Songs of Praise Body Text- song name=', song_name)
            addnode.addbodytext(doctree, slide_group_name, body_text)

        for s in range(len(songs)-2, 1, -1):        #--- process 2 Songs of Praise in reverse order
            song_name, presentation_order = songs[s].rsplit('-', 1) #split the line at '-'
            song_name = song_name.strip()                       #remove leading and trailing spaces
            presentation_order = presentation_order.strip()     #remove leading and trailing spaces
            #print('\nProcess Songs of Praise - song name=', song_name, ' presentation order=', presentation_order)
            doctree = addnode.addsong(doctree, slide_group_name, song_name, presentation_order)   # (slide_group_name, song_name)

    return()
#-------------- End Read and process the songs text file -----------------------------

#------------Start -  Write the new XML set  
def writeXMLSet(doctree):
    import xml.etree.ElementTree as ET

    #--- rename the template set "set" tag
    setNameAttrib = str(getdatetime.nextSunday())	#--- get the "upcoming" Sunday date
    setNameAttrib = setNameAttrib + ' GCCEM Sunday Worship'

    myroot = doctree.getroot()                       #--- XML document tree passed as a parameter

    myroot.attrib = {'name': setNameAttrib}         #--- assign the set name attribute
    print(myroot.tag, myroot.attrib)

    #--- End of processing - write out the modified worship set
    os.chdir(filelist.setpath)   #-- change to the Sets directory
    outputset = setNameAttrib           #--- the set file name is the same as the set name
    doctree.write(outputset)

    #--- write the status complete file
    os.chdir(filelist.bulletinpath)      #-- switch back to the default directory

    updatefinalstatus()             #--- update the current status file upon comletion of processing

    return()
#------------End -  Write the new XML set  

#------------Start Function to split string into list by '.'  
def split_keep(string):
    string = string.split('.')

    for i in range(0, len(string)):
        string[i] = string[i] + '.'
        #print(string[i])
    del string[-1]              #--- remove the last item from the list
    return(string)                  #--- return a list of sentences with '.'
#-----------End Function to split string into list by '.'  

#------------Start Function to extract string after Nth occurrence of specified character   
def split_keep_after(string, char, count):      #--- input string, delimiter, occurrence
    #print('The original string is:' + str(string))

    res = string.split(char, count)[-1] 
  
    #print("The extracted string : " + str(res))

    return(res)                  #--- return the remaining string
#-----------End Function to extract residual characters in string 

#------------Start Function to parse the call to worship   
def parsecalltoworship():
    #-------------- Read the contents of the Call To Worship text file -----------------------------
    textFile = open(filelist.CallToWorshipFileName, 'r', encoding='utf-8',errors='ignore')
    Lines = textFile.readlines()              #--- read the file into a list
    #print(body_text)
    leader_flag = ''
    congregation_flag =''
    body_text = []
    body_text.append(Lines[0] + Lines[1])       #--- get the first 2 lines as the first slide
    #print(body_text)


    #--- determine if this is a responsive reading
    line_count = 0
    for i in Lines:
        #print(i, end = '')
        line_count += 1

        if "leader:" in i.replace(" ", '').replace('\t', '').lower():
            leader_flag ="y"                 #--- set the leader flag
        elif 'congregation:' in i.replace(" ", '').replace('\t', '').lower():
            congregation_flag = 'y'         #--- set the congregation flag
    
    if leader_flag and congregation_flag:   #---  this call to worship is a responsive reading
        body_text = process_responsivereading(Lines, body_text)
    else:
        line_count = 2
        for i in range(2, len(Lines)):
            body_text.append(Lines[line_count])
            line_count += 1

    return(body_text)
#--- end parsecalltoworship
 
def process_responsivereading(Lines, body_text):
    count = 1               #--- position the index after the header lines
    end = len(Lines)
    leader_text = ''
    congregation_text = ''
    all_text = '' 

    while count < end:

        #print('\ncount=', count, 'line=', Lines[count], ' end=', end)
        #line = Lines[count].lower()

    #--- Look for responsive reading -----------------------------
        if 'leader:' in Lines[count].lower():
            for j in range(count, end):
                #print('\nIn leader section - j=', j,  ' text=', Lines[j], ' end=', end)
                leader_text = leader_text + Lines[j]
                if j + 1 == end:
                    body_text.append(leader_text)
                    break
                else:
                    if 'congregation:' in Lines[j+1].lower() or 'alltogether:' in Lines[j+1].lower().replace(" ", ''):
                        #print('\nLeader Body Text =', leader_text)
                        body_text.append(leader_text)
                        leader_text = ''
                        count = j
                        break
                j += 1

        elif "congregation:" in Lines[count].lower():
            #print('\nMatched congregation section - count =', count)
            for j in range (count, end):
                congregation_text = congregation_text + Lines[j]
                if j + 1 == end:
                    body_text.append(congregation_text)
                    break
                else:
                    if 'leader:' in Lines[j+1].lower() or 'alltogether:' in Lines[count+1].lower().replace(" ", ''):
                        #print('\nCongregation Body Text =', congregation_text)
                        body_text.append(congregation_text)
                        congregation_text = ''
                        count = j
                        break
                j += 1

        elif 'alltogether' in Lines[count].lower().replace(" ", ''):
            #print('\nMatched Alltogether section')
            for j in range (count, end):
                all_text = all_text + Lines[j]
                j += 1
            #print('\nAlltogether Body Text =', all_text)
            body_text.append(all_text)
            count = j
        count += 1

    #j = 0
    #for i in body_text:
    #    print('\nj=', j, 'line=', i)
    #    j +=1

    return(body_text)                  #--- return the body_text array
#-----------End Function to parse call to worship 

#------------Start Function to extract string after Nth occurrence of specified character   
def updatefinalstatus():      #--- update the current status  file
    #--- read the bulletin date file
    textFile = open(filelist.BulletinDateFilename, 'r', encoding='utf-8',errors='ignore')
    filedate = textFile.read()              #--- read the file into a string
    textFile.close()
    status_message = 'Bulletin Processing completed for ' + filedate 

    #--- Update the current status file
    textFile = open(filelist.CurrentStatusFilename, 'a', encoding='utf-8',errors='ignore') #--- append to the current status file
    textFile.write(str(status_message))
    textFile.close()


    writehtml.buildhtmlcontent()                                                       #--- create the HTML page to be uploaded to the website

    subprocess.Popen('/root/Dropbox/OpenSongV2/rclone-cron.sh')       #--- run the rclone sync process to upload the set to the website

    print('\nEnd of OpenSong processing - OpenSong Set created ', filelist.SundaySet, 'on ', getdatetime.currentdatetime())

    return()                  #--- return the remaining string
#-----------End Function to extract residual characters in string 