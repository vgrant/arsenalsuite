


#include <qprocess.h>
#include <QDateTime>
#include <qfileinfo.h>
#include <qhostinfo.h>

#include "process.h"

#ifdef Q_OS_WIN
HANDLE hMutex;
#else
#include <unistd.h>
#endif // Q_OS_WIN

bool startup()
{
#ifdef Q_OS_WIN
	hMutex = CreateMutex( NULL, true, L"ABPSMonMutex");
	if (hMutex == NULL) {
		qWarning( "Error: Couldn't create mutex, exiting" );
		return false;
	}
	if( GetLastError() == ERROR_ALREADY_EXISTS ) {
		qWarning( "Error: Another process owns the mutex, exiting" );
		return false;
	}
#endif
	return true;
}

int main( int argc, char * argv [] )
{
	if( !startup() )
		return 1;

	QString procArgs;
#ifdef Q_OS_WIN
	QString procName = "burner.exe";
	bool useGUI = true;
#else
	QString procName = "burner";
	bool useGUI = getenv( "DISPLAY" ) != 0;
#endif
	QString execName = "burner";

	if (!useGUI)
		procArgs = " -nogui";

	if( !initConfig( "burner.ini", "abpsmon.log" ) )
        return -1;

	bool crashMailSent = false;
	QDateTime started = QDateTime::currentDateTime();
	while( 1 ) {
		if( pidsByName( procName ) == 0 ) {
			// Check for recently crashed assburner
			QFileInfo backtrace( "burner.RPT" );
			if( !crashMailSent && backtrace.exists() && backtrace.lastModified() > started ) {
				crashMailSent = true;
				QStringList msg;
				msg << "Assburner Crash, Backtrace and Log attached";
				msg << "Host: " + QHostInfo::localHostName();
				msg << "User: " + getUserName();
				msg << "Time: " + QDateTime::currentDateTime().toString();
				sendEmail( QStringList() << "arenvillanueva@yomogi-soft.com",
					"Assburner Crash",
					msg.join("\n") + "\n",
					"thePipe@yomogi-soft.com",
					QStringList() << "C:/blur/burner/assburner.RPT" << "C:/blur/burner.log" );
			}

			// try to avoid starting a shitload of processes rapidly
			if( started.secsTo(QDateTime::currentDateTime()) > 30 ) {
				QProcess::startDetached( execName+procArgs );
				started = QDateTime::currentDateTime();
				crashMailSent = false;
			}
		}

#ifdef Q_OS_WIN
		Sleep( 1000 );
#else
		sleep( 3 );
#endif // Q_OS_WIN

	}

#ifdef Q_OS_WIN
	CloseHandle( hMutex );
#endif
	return 0;
}


