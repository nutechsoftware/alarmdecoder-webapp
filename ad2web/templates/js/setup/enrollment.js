<script type="text/javascript">
originalNumDevices = '';
states = { 'setConfigBits': 1, 'setConfigBitsDone': 2, 'getCode': 3, 'getCodeDone': 4, 'getPanelType': 5, 'getPanelTypeDone': 6, 'getFirmware': 7, 'getFirmwareDone': 8, 'getDeviceCount': 9, 'getDeviceCountDone': 10, 'getDeviceDetails': 11, 'getDeviceDetailsDone': 12, 'tryTest': 13, 'testDone': 14, 'tryUnlock': 15, 'unlockDone': 16, 'queryLog': 17, 'queryLogDone': 18, 'queryLogDetails': 19, 'queryLogDetailsDone': 20, 'getPartitionCount': 21, 'getPartitionCountDone': 22, 'getPartitionID': 23, 'getPartitionIDDone': 24, 'getPartitionEntries': 25, 'getPartitionEntriesDone': 26, 'getZoneData': 27, 'getZoneDataDone': 28, 'importZones': 29, 'importZonesDone': 30, 'programmingMode': 31, 'programmingModeDone': 32, 'unlockFail': 33, 'doneDone': 35, 'unsupported': 100 };
state = null;
count = 0;
panelType = '';
panelFirmware = '';
iCode = '';
devices = [];
partitionCount = '';
partition_ids = [];
partition_entry_counts = [];
partition_zone_data = [];
numLogEntries = '';
countLogEntries = 0;
retries = 0;
countPartitionIDs = 0;
countPartition = 0;
totalZones = 0;
zoneCount = 0;
zones = [];
partition = '1';
zone_addresses = [];
numberOfDevices = 0;
inProgrammingMode = false;
unlockSlot = 0;
programmingModeRetries = 0;

zone_type_map = { '9': 'Supervised Fire', '00': 'Zone Not Used', '1': 'Entry/Exit #1 Burglary', '2': 'Entry/Exit #2 Burglary', '3': 'Perimiter Burglary', '4': 'Interior, Follower', '5': 'Trouble by Day/Alarm by Night', '6': '24-Hour Silent Alarm', '7': '24-Hour Audible Alarm', '8': '24-Hour Auxiliary Alarm', '10': 'Interior With Delay', '12': 'Monitor Zone', '14': 'Carbon Monoxide', '16': 'Fire w/Verify', '20': 'Arm-STAY', '21': 'Arm-AWAY', '22': 'Disarm', '23': 'No Alarm Response', '24': 'Silent Burglary', '27': 'Access Point', '28': 'Main Logic Board (MLB) Supervision', '29': 'Momentary on Exit', '77': 'KeySwitch', '81': 'AAV Monitor Zone', '90': 'Configurable', '91': 'Configurable' };

zone_device_type_map = { '0': 'Not Used', '1': 'Hardwired', '3': 'Supervised RF Transmitter (RF Type)', '4': 'Unsupervised RF Transmitter (UR Type)', '5': 'RF Button-Type Transmitter (BR Type)', '6': 'Serial Number Polling Loop Device (SL Type)', '7': 'DIP Switch-Type Polling Loop Device', '8': 'Right Loop of DIP Switch Type Device', '9': 'Configurable' };

panelDefinitions = {
    'VISTA-10SE': {0: '31', 31: '31'},
    'VISTA-20SE': {0: '31', 31: '31'},
    'VISTA-10P': {17: '*190', 18: '*191', 19: '*192', 20: '*193', 21: '*194', 22: '*195', 23: '*196' },
    'VISTA-15P': {17: '*190', 18: '*191', 19: '*192', 20: '*193', 21: '*194', 22: '*195', 23: '*196' },
    'VISTA-20P': {17: '*190', 18: '*191', 19: '*192', 20: '*193', 21: '*194', 22: '*195', 23: '*196' },
    'VISTA-21IP': {17: '*190', 18: '*191', 19: '*192', 20: '*193', 21: '*194', 22: '*195', 23: '*196'},
};

partition_map = {
    0: '31', //partition 1
    1: '32', //partition 2
    2: '33',
    3: '34',
    4: '35',
    5: '36',
    6: '37',
    7: '38',
    8: '39'
};


function progress(newVal)
{
    var val = $('#progressbar').progressbar("value") || 0;

    $('#progressbar').progressbar("value", val + newVal);
}

function getStringBetweenChars(str, firstChar, lastChar)
{
    var newStr = str.substring(str.lastIndexOf(firstChar)+1, str.lastIndexOf(lastChar));

    return newStr;
}

function in_array(arr, obj)
{
    return (arr.indexOf(obj) != -1);
}

async function setConfigBits()
{
    state = states['setConfigBits'];
    decoder.emit('keypress', 'CCONFIGBITS=FF05\r\n');
    await sleep(500);
    decoder.emit('keypress', 'K01|006e6b0e4543f531\r\n');
    await sleep(500);
    decoder.emit('keypress', 'K18\r\n'); 
    await sleep(500);
    state = states['setConfigBitsDone'];
}

async function doTest()
{
    state = states['testDone'];
}

async function programmingMode()
{
    state = states['programmingMode'];
    if( iCode != '' && panelType != '' )
    {
        sendString = "K01" + iCode + '800';
        decoder.emit('keypress', sendString);
        decoder.emit('keypress', "K18\r\n");
        await sleep(2000);
    }
}

async function tryUnlock(address)
{
    state = states['tryUnlock'];
    if( inProgrammingMode === false )
    {
        $.alert('Unable to get into programming mode.  Please check your AUI keypad has been removed.');
        state = states['unlockFail'];
    }
    else
    {
        await sleep(1000);
        sendString = "K01" + address + '10';
        decoder.emit('keypress', sendString);
        await sleep(1000);
        decoder.emit('keypress', '*99');
        decoder.emit('keypress', "K18\r\n");
        state = states['unlockDone'];
    }
}

async function wait2seconds()
{
    await sleep(2000);
}

async function getCode()
{
    await sleep(500);
    state = states['getCode'];
    decoder.emit('keypress', 'K01|006f6b0a81\r\n');
    await sleep(500);
}

async function getPanelType()
{
    await sleep(500);
    state = states['getPanelType'];
    decoder.emit('keypress', 'K01|00606b0b4543f531fb436c\r\n');
    await sleep(500);
}

async function getPanelFirmware()
{
    await sleep(500);
    state = states['getFirmware'];
    decoder.emit('keypress', 'K01|00606b0b4543f532fb436c\r\n');
    await sleep(500);
}

async function getDeviceCount()
{
    await sleep(500);
    state = states['getDeviceCount'];
    decoder.emit('keypress', 'K01|00606b0f4361\r\n');
    await sleep(1500);
}

async function getDeviceDetails()
{
    await sleep(500);
    state = states['getDeviceDetails'];
    checkDevices(originalNumDevices);
    await sleep(500);
}

async function getPartitionCount()
{
    await sleep(500);
    state = states['getPartitionCount'];
    decoder.emit('keypress', 'K01|00606b0c4361\r\n');
    await sleep(2500);
}

async function getPartitionIDs(partitionCount)
{
    await sleep(2500);
    state = states['getPartitionID'];
    for( i = 0; i < parseInt(partitionCount); i++)
    {
        await sleep(2500);
        decoder.emit('keypress', 'K01|00606b0c4543f5' + partition_map[i] + 'fb436c\r\n');
        countPartitionIDs++;
    }
}

async function getPartitionEntries(partitionMap)
{
    state = states['getPartitionEntries'];
    for( i = 0; i < partitionMap.length; i++ )
    {
        await sleep(2500);
        decoder.emit('keypress', 'K01|00606b0c4549f5' + asciiToHex(partitionMap[i]) + 'fb4361\r\n');
        countPartition++;
    }
}

async function getZoneData()
{
    getPartitionCount();
    await sleep(2500);
    state = states['getZoneData'];
    var t = $('#zones-table').DataTable();
    t.clear().draw();
    progress(1);
    zones = [];
    zone_addresses = [];
    if( isNaN(partitionCount) )
        return false;

    for( i = 0; i < parseInt(partitionCount); i++ )
    {
        state = states['getZoneData'];
        partition = partition_map[i];
        for( j = 0; j < 30; j++ )
        {
            await sleep(1500);
            decoder.emit('keypress', 'K01|006f620c4549f5' + partition + 'fb4543f5' + asciiToHex(String.fromCharCode(30 + j)) + 'fb436c\r\n');
        }
        progress(Math.floor(100/parseInt(partitionCount)));
    } 
    await sleep(1500);
    state = states['getZoneDataDone'];
}

async function queryLog()
{
    await sleep(500);
    decoder.emit('keypress', 'K01|00606b094549f530fb454af53134fb4361\r\n');
}

function sleep(ms)
{
    return new Promise(resolve=>setTimeout(resolve, ms));
}

async function checkDeviceLogs(numLogs)
{
    countLogEntries = 0;
    for( i = 1; i <= parseInt(numLogs); i++)
    {
        strHex = '';
        if( i < 10 )
        {
            strHex = asciiToHex("00" + i.toString());
        }
        else if( i > 10 && i < 100)
        {
            strHex = asciiToHex("0" + i.toString());
        }
        else
        {
            strHex = asciiToHex(i.toString());
        }
        countLogEntries++;
        decoder.emit('keypress', 'K01|00696b094549f530fb454af53134fb4543f5' + strHex + 'fb436c\r\n');
        await sleep(1500);
    }
}

async function checkDevices(numDevices)
{
    count = 1;
    percent = 0;
    for( i = 1; i <= parseInt(numDevices); i++ )
    {
        strHex = '';

        if( i < 10 )
        {
            strHex = asciiToHex("0" + i.toString());
        }
        else
        {
            strHex = asciiToHex(i.toString());
        }
        decoder.emit('keypress', 'K01|006d6b0f4543f5' + strHex + 'fb436c\r\n');
        count++;
        await sleep(1500);
        percent = Math.floor(20 * (i/ (parseInt(numDevices)) ));
        progress(percent);
    }
}

function hexToAscii(str)
{
    var hex = str.toString();
    var ret = '';
    for( var n = 0; n < hex.length; n += 2)
    {
        ret += String.fromCharCode(parseInt(hex.substr(n, 2), 16));
    }

    return ret;
}

function asciiToHex(str) {
    var arr = [];

    for (var i = 0, l = str.length; i < l; i ++) 
    {
        var hex = Number(str.charCodeAt(i)).toString(16);
        arr.push(hex);
    }

    return arr.join('');
}

function getAUIPrefix(value)
{
    return value.substr(0,2);
}

function getHexVal(value, delimiter)
{
    hexVal = value.substr(value.indexOf(delimiter) + delimiter.length);
    return hexVal;
}

function parseAUIMessage(prefix, value)
{
    if( state == states['getDeviceCount'])
    {
        hexVal = getHexVal(value, "fe");
        ascii = hexToAscii(hexVal);
        originalNumDevices = ascii;
        //subtract '1' to get real number of devices as it's one-based
        retVal = ascii[0] + (ascii[ascii.length-1].charCodeAt(0) - '1'.charCodeAt(0));
        return retVal;
    }
    if( state == states['getCode'] && prefix == '0d' )
    {
        hexVal = value.substr(value.length - 8);
        ascii = hexToAscii(hexVal);
        iCode = ascii;
        return ascii;
    }
    else
    {
        if( state == states['getPanelType'] || state == states['getFirmware'] )
        {
            hexVal = getHexVal(value, "fefeec");
            ascii = hexToAscii(hexVal);
            if( state == states['getPanelType'] )
                panelType = ascii;
            if( state == states['getFirmware'] )
                panelFirmware = ascii;
            return ascii;
        }
        if( state == states['getDeviceDetails'] )
        {
            hexVal = getHexVal(value, "fefeec");
            details = {'address': hexToAscii(hexVal.substr(0,4)), 'type': (hexVal.substr(4,4) == "0034" ? "Keypad" : "Unknown")};
            devices.push(details);
            return details;
        }
        if( state == states['queryLog'] )
        {
            hexVal = getHexVal(value, "fefefe");
            ascii = hexToAscii(hexVal);
            return ascii;
        }
        if( state == states['queryLogDetails'] )
        {
            hexVal = getHexVal(value, "fefefefeec");
            ascii = hexToAscii(hexVal);
            return ascii;
        }
        if( state == states['getPartitionCount'] )
        {
            hexVal = getHexVal(value, "fe");
            ascii = hexToAscii(hexVal);
            return ascii;
        }
        if( state == states['getPartitionID'] )
        {
            hexVal = getHexVal(value, "fefeec");
            ascii = hexToAscii(hexVal);
            return ascii;
        }
        if( state == states['getPartitionEntries'] )
        {
            hexVal = getHexVal(value, "fefe");
            ascii = hexToAscii(hexVal);
            return ascii;
        }
        if( state == states['getZoneData'] )
        {
            if( value.indexOf("fefefeec") == -1 )
            {
                return null;
            }
            hexVal = getHexVal(value, "fefefeec");
            if( hexVal.length )
            {
                arr = hexVal.split("00");
                if( arr.length < 3 )
                    return null;
                
                if (arr.length > 0 && arr[0].length % 2){
                    arr[0] = hexVal.substring(0, arr[0].length +1);
                    arr[1] = arr[1].substring(1, arr[1].length);
                }

                address = hexToAscii(arr[0]);
                zone_type = hexToAscii(arr[1]);
                zone_device_type = hexToAscii(arr[2]);
                if( arr.length == 4 )
                    zone_name = (arr[3] === 'undefined' ? '' : hexToAscii(arr[3]) );
                else
                    zone_name = '';
                
                if( parseInt(asciiToHex(zone_device_type)) >= 31 )
                {
                    zone = { 'address': address, 'zone_type': zone_type, 'zone_device_type': zone_device_type, 'zone_name': zone_name };
                    if( !in_array(zone_addresses, address) )
                    {
                        zones.push(zone);
                        zone_addresses.push(address);
                    }
                    return zone;
                }
                else
                    return null;
            }
            return null;
        }
    }
}

function populateZones(zones)
{
    z = JSON.stringify(zones);
    state = states['importZones'];
    var t = $('#zones-table').DataTable();
    $.ajax({
        type: "POST",
        url: "{{ url_for('zones.import_zone') }}",
        data:  z,
        contentType: 'application/json;charset=UTF-8',
        success: function(msg) {
            state = states['importZonesDone'];
            $('#zone_scanning').stop();
            $('#zone_scanning').hide();
            if( msg['success'] != 0 )
            {
                a = msg['success'];

                for( var key in a )
                {
                    var entry = a[key];
                    t.row.add(["<a href='/settings/zones/edit/" + entry['zone_id'] + "'>" + entry['zone_id'] + "</a>", entry['name'], entry['description'], "<a href='/settings/zones/remove/" + entry['zone_id'] + "'><img style='text-align: center; float: right; margin-right: 15px;' src='{{ url_for('static', filename='img/red_x.png') }}'/></a>"]).draw();
                }
            }
            else
                alert("No zones found, possible unsupported.");

            $('.progress_label').hide();
            $('#progressbar').hide();
        }
    });
}
</script>
