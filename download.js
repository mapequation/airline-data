const shell = require('shelljs');
const program = require('commander');
const _ = require('lodash');
const chalk = require('chalk');


class Logger {

    constructor() {
        this.indentLevel = 0;
    }

    push() {
        ++this.indentLevel;
    }
    pop() {
        this.indentLevel = Math.max(0, this.indentLevel - 1);
    }
    indentString() {
        return '  '.repeat(this.indentLevel);
    }
    colored(msg) {
        const lvl = Math.min(this.indentLevel, 3);
        return [chalk.magenta, chalk.cyan, chalk.blue, (msg) => msg][lvl](msg);
    }
    info(msg) {
        console.log(`${this.indentString()}${this.colored(msg)}`);
    }
    log(msg) {
        console.log(`${this.indentString()}${msg}`);
    }
    notice(msg) {
        console.error(`${this.indentString()}Notice: ${chalk.yellow(msg)}`);
    }
    success(msg) {
        console.error(`${this.indentString()}${chalk.green(msg)}`);
    }
    error(msg) {
        console.error(`${this.indentString()}${chalk.red(msg)}`);
    }
}

l = new Logger();


function parseRange(args) {
    return _.flatten(args.split(',')
        .map(values => {
            const [v1, v2] = values.split('..');
            const vStart = Number(v1);
            const vEnd = Number(v2 || v1) + 1;
            return _.range(vStart, vEnd);
        }));
}

program
    .version('1.0.0')
    .usage('[options]')
    .option('-y, --year <years>', 'Select years from 1993-2017 (e.g. -y 1995..2000,2010,2015)', parseRange)
    .option('-q, --quarter <quarters>', 'Select quarters from 1-4 (e.g. -q 1,4. Default 1..4)', parseRange)
    .option('-f, --force', 'Force overwrite even if file exist')
    .option('-m, --minimal', 'Download minimal number of data columns')
    .option('-t, --type <type>', 'Type of data, one of Coupon or Market, default Coupon')
    .option('-d, --debug', 'Run test')
    .parse(process.argv);

if (program.debug) {
    shell.cd('data');
    shell.echo(shell.pwd())
    shell.ls('*.zip').forEach(file => {
        shell.echo(file);
    });
    shell.exit(0);
}

if (!program.year) {
    program.help();
}
if (!program.quarter) {
    program.quarter = [1,2,3,4];
}
if (!program.type) {
    program.type = 'Coupon';
}

if (_.filter(program.year, year => year >= 1993 && year <= 2017).length !== program.year.length) {
    l.error(`Not all years in range: ${program.year}`);
    program.help();
}
if (_.filter(program.quarter, quarter => quarter >= 1 && quarter <= 4).length !== program.quarter.length) {
    l.error(`Not all quarters in range: ${program.quarter}`);
    program.help();
}
if (program.type !== 'Coupon' && program.type !== 'Market') {
    l.error(`Type not valid: ${program.type}`);
    program.help();
}

l.info(chalk`Try download and extract ${program.type} data from years {bold ${program.year}} and quarters {bold ${program.quarter}}...`);

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const getFilename = ({year, quarter}) => `${year}_${quarter}_${program.type}${program.minimal ? '_min' : ''}`;
const getExtractedFilename = ({year, quarter}) => `Origin_and_Destination_Survey_DB1B${program.type}_${year}_${quarter}`;

const wgetMinimalData = ({year, quarter}) =>
`wget -O ${getFilename({year, quarter})}.zip --post-data="UserTableName=DB1BCoupon&DBShortName=Origin_and_Destination_Survey&RawDataTable=T_DB1B_COUPON&sqlstr=+SELECT+ITIN_ID%2CMKT_ID%2CYEAR%2CORIGIN_AIRPORT_ID%2CQUARTER%2CDEST_AIRPORT_ID+FROM++T_DB1B_COUPON+WHERE+Quarter+%3D${quarter}+AND+YEAR%3D${year}&varlist=ITIN_ID%2CMKT_ID%2CYEAR%2CORIGIN_AIRPORT_ID%2CQUARTER%2CDEST_AIRPORT_ID&grouplist=&suml=&sumRegion=&filter1=title%3D&filter2=title%3D&geo=All%A0&time=Q+${quarter}&timename=Quarter&GEOGRAPHY=All&XYEAR=${year}&FREQUENCY=${quarter}&document=Y&VarName=ITIN_ID&VarDesc=ItinID&VarType=Num&VarName=MKT_ID&VarDesc=MktID&VarType=Num&VarDesc=SeqNum&VarType=Num&VarDesc=Coupons&VarType=Num&VarName=YEAR&VarDesc=Year&VarType=Num&VarName=ORIGIN_AIRPORT_ID&VarDesc=OriginAirportID&VarType=Num&VarDesc=OriginAirportSeqID&VarType=Num&VarDesc=OriginCityMarketID&VarType=Num&VarName=QUARTER&VarDesc=Quarter&VarType=Num&VarDesc=Origin&VarType=Char&VarDesc=OriginCountry&VarType=Char&VarDesc=OriginStateFips&VarType=Char&VarDesc=OriginState&VarType=Char&VarDesc=OriginStateName&VarType=Char&VarDesc=OriginWac&VarType=Num&VarName=DEST_AIRPORT_ID&VarDesc=DestAirportID&VarType=Num&VarDesc=DestAirportSeqID&VarType=Num&VarDesc=DestCityMarketID&VarType=Num&VarDesc=Dest&VarType=Char&VarDesc=DestCountry&VarType=Char&VarDesc=DestStateFips&VarType=Char&VarDesc=DestState&VarType=Char&VarDesc=DestStateName&VarType=Char&VarDesc=DestWac&VarType=Num&VarDesc=Break&VarType=Char&VarDesc=CouponType&VarType=Char&VarDesc=TkCarrier&VarType=Char&VarDesc=OpCarrier&VarType=Char&VarDesc=RPCarrier&VarType=Char&VarDesc=Passengers&VarType=Num&VarDesc=FareClass&VarType=Char&VarDesc=Distance&VarType=Num&VarDesc=DistanceGroup&VarType=Num&VarDesc=Gateway&VarType=Num&VarDesc=ItinGeoType&VarType=Num&VarDesc=CouponGeoType&VarType=Num" https://www.transtats.bts.gov/DownLoad_Table.asp?Table_ID=272`;

const wgetPrezipped = ({year, quarter}) => `wget -O ${getFilename({year, quarter})}.zip https://transtats.bts.gov/PREZIP/Origin_and_Destination_Survey_DB1BCoupon_${year}_${quarter}.zip`

function downloadFile({year, quarter}) {
    const filename = `${getFilename({year, quarter})}`;
    const command = program.minimal ? wgetMinimalData({ year, quarter }) : wgetPrezipped({ year, quarter });
    return new Promise((resolve, reject) => {
        const child = shell.exec(command, { async: true, silent: true }, (code, stdout, stderr) => {
            if (code !== 0) {
                l.error(`Error code ${code}:`);
                l.log(stdout);
                l.error(stderr);
                reject(code);
            } else {
                // console.log(stdout);
                // console.error(chalk.red(stderr));
                console.log('');
                l.success(`${filename}.zip downloaded!`);
                resolve(code);
            }
        });
        child.stdout.on('data', (data) => {
            // const progressMatch = /\d+%/.exec(data);
            const progressMatch = new RegExp(`d+%`).exec(data);
            if (progressMatch) {
                process.stdout.write(`\r${l.indentString()}Download progress: ${chalk.white(progressMatch[0])}`);
            }
            
        });
        child.stderr.on('data', (data) => {
            const progressMatch = /\d+%/.exec(data);
            if (progressMatch) {
                process.stdout.write(`\r${l.indentString()}Download progress: ${chalk.white(progressMatch[0])}`);
            }
        });
    })
}

function extractFile({year, quarter}) {
    const filename = `${getFilename({year, quarter})}.zip`;
    const extractedCsvFilename = `${getExtractedFilename({year, quarter})}.csv`;
    const csvFilename = `${getFilename({year, quarter})}.csv`;
    return new Promise((resolve, reject) => {
        if (!shell.test('-f', filename)) {
            const error = `Missing file to extract at ${shell.pwd()}/${filename}`;
            l.error(error);
            return reject(new Error(error));
        }
        const child = shell.exec(`unzip -o ${filename}`, { async: true }, (code, stdout, stderr) => {
            if (code !== 0) {
                l.error(`Error extracting file: ${code}`);
                reject(code);
            } else {
                shell.mv(extractedCsvFilename, csvFilename);
                l.success(`${filename} extracted to ${csvFilename}!`);
                resolve(code);
            }
        });
    });
}

function fixCsv({year, quarter}) {
    const filename = `${getFilename({year, quarter})}.csv`;
    l.log(`Fix ${filename}.csv...`);
    return new Promise((resolve, reject) => {
        if (!shell.test('-f', filename)) {
            const error = `Missing file to fix at ${shell.pwd()}/${filename}`;
            l.error(error);
            return reject(new Error(error));
        }
        const header = shell.head({'-n': 1}, filename);
        const isCommaLast = header.slice(-2) == ",\n";
        if (isCommaLast) {
            l.info(`Remove last comma in ${filename}...`);
            const child = shell.exec(`sed -i .bak 's/.$//' ${filename}`, { async: true }, (code, stdout, stderr) => {
                if (code !== 0) {
                    l.error(`Error fixing csv ${code}:`);
                    reject(code);
                } else {
                    shell.rm('-f', `${filename}.bak`);
                    l.success(`${filename}.csv fixed!`);
                    resolve(code);
                }
            });
        }
        else {
            l.log(`${filename} doesn't need fix`);
            resolve(0);
        }
    });
}

async function download(years, quarters) {
    shell.mkdir('-p', 'data');
    shell.cd('data');
    for (let i = 0; i < years.length; ++i) {
        const year = years[i];
        l.push();
        l.log(`Year ${chalk.bold(year)}...`);
        for (let j = 0; j < quarters.length; ++j) {
            l.push();
            const quarter = quarters[j];
            const filename = `${getFilename({year, quarter})}`;
            l.log(`Quarter ${chalk.bold(quarter)}...`);
            {
                l.push();
                l.log(`Download ${filename}.zip...`);
                const zipExists = shell.test('-f', `${filename}.zip`);
                try {
                    if (!zipExists || program.force) {
                        if (zipExists) {
                            l.notice(`- Zip already exists, forcing overwrite...`);
                        }
                        await downloadFile({ year, quarter });
                    }
                    else {
                        l.notice(`- Zip already exists, use -f/--force to overwrite`);
                    }
                }
                catch (err) {
                    l.error(`Error downloading file: ${err}`);
                }
                try {
                    const csvExists = shell.test('-f', `${filename}.csv`);
                    l.log(`Extract ${filename}.zip...`);
                    if (!csvExists || program.force) {
                        if (csvExists) {
                            l.notice(`- Csv already exists, forcing overwrite...`);
                        }
                        await extractFile({year, quarter});
                    }
                    else {
                        l.notice(`- Csv already exists, use -f/--force to overwrite`);
                    }
                }
                catch (err) {
                    l.error('Error extracting data:', err);
                }
                try {
                    await fixCsv({year, quarter});
                }
                catch (err) {
                    l.error(`Error fixing data: ${err}`);
                }
                await wait(500);
                l.pop();
            }
            l.pop();
        }
        l.pop();
    }
}

download(program.year, program.quarter);

