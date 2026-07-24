# Update Guide

## Check Only

```powershell
python scripts/update_skill.py --target <installed-skill-directory>
```

## Apply GitHub Update

```powershell
python scripts/update_skill.py --target <installed-skill-directory> --apply
```

## Apply Gitee Update

```powershell
python scripts/update_skill.py --source https://gitee.com/tigerran/loop-engineering-bootstrap.git --target <installed-skill-directory> --apply
```

The updater clones into a temporary directory, renames the current Skill to a
timestamped backup, copies the new version, and restores the backup if copying
fails. Restart the host Agent after a successful update.

The updater does not modify the target project's `.agent` data. Updating the
Skill and upgrading a project's generated Loop Engineering layer are separate
operations; run the Skill in the target project to review and migrate its
`.agent` files.
