/*
 *
 * Copyright 2003, 2004 Blur Studio Inc.
 *
 * This file is part of the Resin software package.
 *
 * Resin is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Resin is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Resin; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

#ifndef SCENE_DIALOG_H
#define SCENE_DIALOG_H

#include "classesui.h"

#include "ui_scenedialogui.h"
#include "shotgroup.h"

class CLASSESUI_EXPORT SceneDialog : public QDialog, public Ui::SceneDialogUI
{
Q_OBJECT
public:
	SceneDialog( QWidget * parent=0 );

	ShotGroup shotGroup();

	void setShotGroup( ShotGroup scene );

	void accept();

protected:

	ShotGroup mShotGroup;
};

#endif // SCENE_DIALOG_H

